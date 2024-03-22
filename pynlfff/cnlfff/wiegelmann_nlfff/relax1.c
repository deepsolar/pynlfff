/*
 * @Description: https://doi.org/10.1007/s11207-012-9966-z
 * @Author: Thomas Wiegelmann (wiegelmann@mps.mpg.de)
 * @Date: 
 * @LastEditors: Thomas Wiegelmann (wiegelmann@mps.mpg.de)
 * @LastEditTime: 
*/

/* relax1.c */
#include <stdio.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>

#ifdef _OPENMP
#include <omp.h>
#endif
/* Global Variables */
FILE *streamw, *initfile;
double Cmn[102][102], lmn[102][102], rmn[102][102];
double Lx, Ly, Lz, alpha, pi, q1;
double L1, L2, L3;
double *t, *xt, *yt, *zt, *absB, *t2, *xyzB, *refB;
double *x, *y, *z;
double *Bx, *By, *Bz;
/* double *B; */
double *Bx1, *By1, *Bz1, *Bx2, *By2, *Bz2;
float *VxBx, *VxBy, *VxBz, *Rotvx, *Rotvy, *Rotvz;
float *Jx, *Jy, *Jz, *Vx, *Vy, *Vz;
float *Jx1, *Jy1, *Jz1;
float *ox, *oy, *oz, *oxbx, *oxby, *oxbz, *odotb, *DivB;
float *oxjx, *oxjy, *oxjz, *Fx, *Fy, *Fz;
double *Bxorig, *Byorig, *Bzorig, *mask;
/* double *Bxana, *Byana, *Bzana; */
float *oxa, *oya, *oza, *oxb, *oyb, *ozb; /*, *ux, *uy, *uz, *u; */
double *wa0, *wb0;
float *wax, *way, *waz, *wbx, *wby, *wbz;
double dt, length;
double C;
double dx, dy, dz, h;
double mu0, rmu0, Ls, gausT, rmu0gausT, mue;
double Bave, Lxyave;
int maxm, maxn;
int maxsteps, max2;
int nx, ny, nz, nynz, nxnynz, nd, nxmax, nymax, nzmax;
int calcb, maxit, firsttime, m0, n0;
int nxnynz1, nxnynz2, diagstep;
#include "globals.h"

void init(double alpha);
void calculateJxB();
void classicrelax();
double split();
double bx(double x0, double y0, double z0);
double by(double x0, double y0, double z0);
double bz(double x0, double y0, double z0);
double babs(double x0, double y0, double z0);
/*
double gradx(double *f, int i);
double grady(double *f, int i);
double gradz(double *f, int i);
*/
double calculateL();
double calculateLi();
double zeit(void);
void loadboundary();
void loadvectormag();
void loadvectormag2();

void green();
#define TEST1 printf("\n\n this is a define test \n")
/* ---------- Routine fuer CPU Zeitmessung -------------- */
double zeit(void)
{
    static double tima = 0.;
    double tim, t;
    tim = (double)clock() / CLOCKS_PER_SEC;
    t = tim - tima;
    tima = tim;
    return (t);
}
/* ------------------------------------------------------- */

/****************************************************/
/******* MAIN PROGRAM   *****************************/
/****************************************************/
int main(int argc, char *argv[])
{
    /* FILE *streamw2, *streamw3; */
    /* int it2, m1,n1; */
    // printf("\n\n ==============relax run now================== \n");
    int i, it, ix, iy, iz;
    int i1, i2, i3;
    int /* count, */ zaehlv;
    /* double x0, y0, z0, bx0, by0 , bz0 ; */
    /* double divB, totB, divJ, totJ, totV; */
    /* double maxdivB, maxJ, maxV,  dummy3, minJ, maxB;*/
    double dummy, dummy1, dummy2;
    double nu, /* nu0, oldtotV,*/ L, Li;
    double time1, timetot;
    double mue2, nave, Bave;
    double oldL, w2, w, Llimit;
    double nue;
    int boundary, restore;
    /* double R,T0,g; */

    double prevL, newL, gradL;
    float *prof, *xprof, *yprof, *zprof;
    int statcount;
    char leer[25];
    L = oldL = w2 = w = Llimit = L1 = L2 = L3 = 0.0;
    statcount = 0;
#ifdef _OPENMP
    printf("\n\n Compiled by OpenMP \n");
#endif

    /********************************************************/
    if (argc < 3)
    {
        printf("\n\n Input **calcb ** and **maxit**  \n\n");
        exit(1);
    }
    if (!sscanf(argv[1], "%i", &calcb))
    {
        printf("\n 1. parameter **calcb** must be an integer number \n");
        exit(1);
    }
    if (!sscanf(argv[2], "%i", &maxit))
    {
        printf("\n 2. parameter **maxit** must be an integer number \n");
        exit(1);
    }
    printf("\n\n argv[0]: \t %s", argv[0]);
    printf("\n argv[1]: \t %s", argv[1]);
    printf("\n argv[2]: \t %s", argv[2]);
    printf("\n calcb= %i \t maxit= %i", calcb, maxit);
    /********************************************************/
    /* if((streamw = fopen("startpot.mark","w")) == NULL) { printf("\n Error startpot.mark"); exit(1);}
fclose(streamw); */
    timetot = 0.0;
    q1 = 1.0;
    mu0 = 1.2566e-6;
    rmu0 = 1. / mu0;
    /* Length in Mm */
    /* Ls=1.0e6; */
    Ls = 1.0;
    gausT = 0.0001; /* Gauss to Tesla */
    rmu0gausT = rmu0 * gausT;
    printf("\n\n Ls=%lf \t mu0= %lf", Ls, mu0);
    if ((initfile = fopen("grid.ini", "r")) == NULL)
    {
        printf("\n Error");
        exit(1);
    }
    fscanf(initfile, "%s %i", &leer, &nx);
    fscanf(initfile, "%s %i", &leer, &ny);
    fscanf(initfile, "%s %i", &leer, &nz);
    fscanf(initfile, "%s %lf", &leer, &mue);
    fscanf(initfile, "%s %i", &leer, &nd);
    fclose(initfile);
    /* mue=mue*1.0e11; */
    printf("\n nx= %i, ny=%i , nz= %i \n", nx, ny, nz);
    nynz = ny * nz;
    nxnynz = nx * ny * nz;
    nxnynz1 = (nx - 0) * (ny - 0) * (nz - 0);
    nxnynz2 = (nx - 0) * (ny - 0) * (nz - 0);
    zaehlv = 0;
    x = (double *)calloc(nx, sizeof(double));
    y = (double *)calloc(ny, sizeof(double));
    z = (double *)calloc(nz, sizeof(double));

    Bxorig = (double *)calloc(nx * ny, sizeof(double));
    Byorig = (double *)calloc(nx * ny, sizeof(double));
    Bzorig = (double *)calloc(nx * ny, sizeof(double));
    mask = (double *)calloc(nx * ny, sizeof(double));
    Bx = (double *)calloc(nxnynz, sizeof(double));
    By = (double *)calloc(nxnynz, sizeof(double));
    Bz = (double *)calloc(nxnynz, sizeof(double));
    /* B = (double *) calloc(3*nxnynz, sizeof(double)); */
    printf("\n\n Size of double: %i", sizeof(double));
    printf("\n nxnynz * Size of double: %i", nxnynz * sizeof(double));
    printf("\n nxnynz * Size of float: %i", nxnynz * sizeof(float));
    Bx1 = (double *)calloc(nxnynz, sizeof(double));
    By1 = (double *)calloc(nxnynz, sizeof(double));
    Bz1 = (double *)calloc(nxnynz, sizeof(double));

    Bx2 = (double *)calloc(nxnynz, sizeof(double));
    By2 = (double *)calloc(nxnynz, sizeof(double));
    Bz2 = (double *)calloc(nxnynz, sizeof(double));
    /*
Jx =(float *) calloc(nxnynz, sizeof(float));
Jy =(float *) calloc(nxnynz, sizeof(float));
Jz =(float *) calloc(nxnynz, sizeof(float));
Jx1 =(float *) calloc(nxnynz, sizeof(float));
Jy1 =(float *) calloc(nxnynz, sizeof(float));
Jz1 =(float *) calloc(nxnynz, sizeof(float));

Vx =(float *) calloc(nxnynz, sizeof(float));
Vy =(float *) calloc(nxnynz, sizeof(float));
Vz =(float *) calloc(nxnynz, sizeof(float));

VxBx =(float *) calloc(nxnynz, sizeof(float));
VxBy =(float *) calloc(nxnynz, sizeof(float));
VxBz =(float *) calloc(nxnynz, sizeof(float));

Rotvx =(float *) calloc(nxnynz, sizeof(float));
Rotvy =(float *) calloc(nxnynz, sizeof(float));
Rotvz =(float *) calloc(nxnynz, sizeof(float));
*/

    /*********************************************************/
    ox = (float *)calloc(nxnynz, sizeof(float));
    oy = (float *)calloc(nxnynz, sizeof(float));
    oz = (float *)calloc(nxnynz, sizeof(float));
    oxbx = (float *)calloc(nxnynz, sizeof(float));
    oxby = (float *)calloc(nxnynz, sizeof(float));
    oxbz = (float *)calloc(nxnynz, sizeof(float));
    odotb = (float *)calloc(nxnynz, sizeof(float));
    DivB = (float *)calloc(nxnynz, sizeof(float));
    oxjx = (float *)calloc(nxnynz, sizeof(float));
    oxjy = (float *)calloc(nxnynz, sizeof(float));
    oxjz = (float *)calloc(nxnynz, sizeof(float));
    Fx = (float *)calloc(nxnynz, sizeof(float));
    Fy = (float *)calloc(nxnynz, sizeof(float));
    Fz = (float *)calloc(nxnynz, sizeof(float));
    oxa = (float *)calloc(nxnynz, sizeof(float));
    oya = (float *)calloc(nxnynz, sizeof(float));
    oza = (float *)calloc(nxnynz, sizeof(float));
    oxb = (float *)calloc(nxnynz, sizeof(float));
    oyb = (float *)calloc(nxnynz, sizeof(float));
    ozb = (float *)calloc(nxnynz, sizeof(float));
    /*
ux =(double *) calloc(nxnynz, sizeof(double));
uy =(double *) calloc(nxnynz, sizeof(double));
uz =(double *) calloc(nxnynz, sizeof(double));
u =(double *) calloc(nxnynz, sizeof(double));
*/
    wax = (float *)calloc(nxnynz, sizeof(float));
    way = (float *)calloc(nxnynz, sizeof(float));
    waz = (float *)calloc(nxnynz, sizeof(float));
    wa0 = (double *)calloc(nxnynz, sizeof(double));
    wbx = (float *)calloc(nxnynz, sizeof(float));
    wby = (float *)calloc(nxnynz, sizeof(float));
    wbz = (float *)calloc(nxnynz, sizeof(float));
    wb0 = (double *)calloc(nxnynz, sizeof(double));

    /************************ run green solver ******************************************/
    if (calcb == 22)
    {
        printf("\n Computing Potential field \n");
        green();
        calcb = 20;
    }
    if (calcb == 23)
    {
        printf("\n Computing Potential field \n");
        green();
        exit(1);
    }
/*************************************************************************************/
#ifdef _OPENMP
#pragma omp parallel for private(i)
#endif
    for (i = 0; i < nxnynz; i++)
    {
        ox[i] = oy[i] = oz[i] = oxbx[i] = oxby[i] = oxbz[i] = odotb[i] = DivB[i] = 0.0;
        oxjx[i] = oxjy[i] = oxjz[i] = Fx[i] = Fy[i] = Fz[i] = 0.0;
    }
    /************************************************************************************/

    if ((streamw = fopen("prot.log", "w")) == NULL)
    {
        printf("\n Error prot.log");
        exit(1);
    }
    fclose(streamw);
    alpha = 0.0;
    if (calcb == 1 && maxit == -1)
    {
        printf("\n Input alpha: ");
        scanf("%lf", &alpha);
    }
    printf("\n\n alpha = %lf", alpha);

    /* calcb=0; */ /* 0 read bin, 1 calculate linear B, 2 read asci */
    /* Read boundary layer */
    /*
if((initfile = fopen("nd.ini","r")) == NULL) { printf("\n Error nd.ini"); exit(1);}
fscanf(initfile,"%s %i",&leer,&nd);
fscanf(initfile,"%s %i",&leer,&nxmax);
fscanf(initfile,"%s %i",&leer,&nymax);
fscanf(initfile,"%s %i",&leer,&nzmax);
fclose(initfile);
*/
    nxmax = nx;
    nymax = ny;
    nzmax = nz;

    if (calcb == 1)
    {
        init(alpha); /* Load Linear Force Free Parameters + calculate Field */
    }
    else /******* Read from bin *********************************/
    {
        if ((streamw = fopen("B0.bin", "rb")) == NULL)
        {
            printf("\n Error B.bin");
            exit(1);
        }
        fread(Bx, sizeof(double) * nxnynz, 1, streamw);
        fread(By, sizeof(double) * nxnynz, 1, streamw);
        fread(Bz, sizeof(double) * nxnynz, 1, streamw);
        printf("\n B0.bin Read finished \n");
        nave = sqrt(1.0 * (nx - 2 * nd - 1) * (ny - 2 * nd - 1));
        Lx = 1.0 * (nx - 1) / nave;
        Ly = 1.0 * (ny - 1) / nave;
        Lz = 1.0 * (nz - 1) / nave;
    }
    printf("\n Lx= %lf \t Ly= %lf \t Lz= %lf", Lx, Ly, Lz);
    printf("\n nx= %i \t ny= %i \t nz= %i", nx, ny, nz);
    dx = dy = dz = Lx / (nx - 1); /* (nxmax-1); */

    printf("\n\n Lx = %.2lf \t Ly= %.2lf \t Lz= %.2lf ", Lx, Ly, Lz);
    printf("\n dx = %.5lf \t dy= %.5lf \t dz= %.5lf \n\n", dx, dy, dz);
    /************************************************************************************/
    if (calcb == 0 || calcb == 10 || calcb == 11)
    {
        loadboundary();
    }
    if ((calcb == 20) || (calcb == 21))
    {
        loadvectormag();
    }

    if (calcb == 40)
    {
        printf("\n ***************** NEW EXPERIMENTAL code ************** ");
        printf("\n ***************** Relax also boundary   ************** ");
        printf("\n ***************** Load vecmag slowly    ************** ");

        for (i = 0; i < nx * ny; i++)
        {
            Bxorig[i] = Byorig[i] = Bzorig[i] = 0.0;
            mask[i] = 1.0;
        }
        loadvectormag2();
        // loadvectormag();

        if ((streamw = fopen("mask.dat", "r")) == NULL)
        {
            printf("\n Error mask.dat");
            exit(1);
        }
        for (iy = 0; iy < ny; iy++)
            for (ix = 0; ix < nx; ix++)
            {
                i1 = ny * ix + iy;
                fscanf(streamw, "%lf", &dummy1);
                mask[i1] = dummy1;
            }
        fclose(streamw);
        nue = 1.0;
        boundary = 0;
        if ((initfile = fopen("boundary.ini", "r")) == NULL)
        {
            printf("\n No File boundary.ini ");
            printf("\n Use default values:");
/* exit(1); */}
else
{
    printf("\n boundary.ini exists \n");
    fscanf(initfile, "%s %lf", &leer, &nue);
    fscanf(initfile, "%s %i", &leer, &boundary);
    fclose(initfile);
    printf("\n nue= %lf, \t boundary= %i", nue, boundary);
}
    }
    /*
if (calcb==15)
{
loadboundary2(0.0);
w2=1.0;
Llimit=5.0;
}
*/
    if (1 == 1) /* norm B, only inner Region */
    {
        iz = 0;
        Bave = 0.0;
        for (ix = nd; ix < nx - nd; ix++)
            for (iy = nd; iy < ny - nd; iy++)
            {
                i = nynz * ix + nz * iy + iz;
                Bave = Bave + sqrt(Bx[i] * Bx[i] + By[i] * By[i] + Bz[i] * Bz[i]);
            }
        Bave = Bave / (nx - 2 * nd) / (ny - 2 * nd);
        printf("\n Bave= %lf", Bave);
#ifdef _OPENMP
#pragma omp parallel for private(i)
#endif
        for (i = 0; i < nxnynz; i++)
        {
            Bx[i] = Bx[i] / Bave;
            By[i] = By[i] / Bave;
            Bz[i] = Bz[i] / Bave;
        }
        for (i = 0; i < nx * ny; i++)
        {
            Bxorig[i] = Bxorig[i] / Bave;
            Byorig[i] = Byorig[i] / Bave;
            Bzorig[i] = Bzorig[i] / Bave;
        }
    }

    /* Read analytic field for comparison */
    if (calcb == 10)
    {
        printf("\n\n *** Classic Relaxation-Code *** \n\n");
        printf("\n\n *** Disabled in this Version *** \n\n");
        exit(1);
    }
    if (calcb == 0)
    {
        printf("\n\n *** Optimisation-Code *** \n\n");
    }
    if (calcb == 11)
    {
        printf("\n\n *** Optimisation-Code *** ");
        printf("\n NOT FORCE FREE. Calc Forces from Bana (Test for Magara MHD) \n\n");
        printf("\n\n *** Disabled in this Version *** \n\n");
        exit(1);
    }
    if (calcb == 15)
    {
        printf("\n\n *** Optimisation-Code, Sress + Relax *** \n\n");
        printf("\n\n *** Disabled in this Version *** \n\n");
        exit(1);
    }
    if (calcb == 20)
    {
        printf("\n\n *** Optimisation-Code, Only photosphere loaded *** \n\n");
    }
    if (calcb == 21)
    {
        printf("\n\n *** Optimisation-Code, Only photosphere loaded *** ");
        printf("\n NOT FORCE FREE. Calc Forces from Bana (Test for Magara MHD) \n\n");
        printf("\n\n *** Disabled in this Version *** \n\n");
        exit(1);
    }

/* Bana=B0 */
/*
for(i=0;i<nxnynz;i++)
{
Bxana[i]=Bx[i];
Byana[i]=By[i];
Bzana[i]=Bz[i];
}
*/
/*
if((streamw = fopen("Bana.bin","rb")) == NULL) { printf("\n Error Bana.bin"); exit(1);}
fread(B,sizeof(double)*3*nxnynz,1,streamw);
printf("\t Read finished ");

#ifdef _OPENMP
#pragma omp parallel for private (i)
#endif
for(i=0;i<nxnynz;i++)
{
Bxana[i]=B[i];
Byana[i]=B[i+nxnynz];
Bzana[i]=B[i+2*nxnynz];
}
*/
#ifdef _OPENMP
#pragma omp parallel for private(i)
#endif
    for (i = 0; i < nxnynz; i++)
    {
        Bx1[i] = Bx2[i] = Bx[i];
        By1[i] = By2[i] = By[i];
        Bz1[i] = Bz2[i] = Bz[i];
        /* Jx[i]=Jy[i]=Jz[i]=Vx[i]=Vy[i]=Vz[i]=VxBx[i]=VxBy[i]=VxBz[i]=0.0;
Rotvx[i]=Rotvy[i]=Rotvz[i]=0.0; */
    }
    printf("\n nx= %i, ny=%i, nz=%i, nynz=%i, nxnynz=%i \n", nx, ny, nz, nynz, nxnynz);

    /**************************************************************************************/
    /************************ Relaxation   Loop                ****************************/
    /**************************************************************************************/
    /* maxit=51; */
    printf("\n calcb= %i", calcb);
    printf("\n maxit= %i", maxit);
    h = dx;
    /*
if((streamw = fopen("start.mark","w")) == NULL) { printf("\n Error start.mark"); exit(1);}
fclose(streamw);
*/
    /********** Read P *************/
    /*
if(1==2)
{
if((streamw = fopen("u.bin","rb")) == NULL) { printf("\n Error u.bin"); exit(1);}
fread(u,sizeof(double)*1*nxnynz,1,streamw);
printf("\n Read P finished ");
T0=3.0e6;
R=8380.0;
g=1.00*270.0;

for(ix=0;ix<nx-0;ix++)
for(iy=0;iy<ny-0;iy++)
for(iz=0;iz<nz-0;iz++)
{
i=ix*nynz+iy*nz+iz;
ux[i]=-GRADX(u,i);
uy[i]=-GRADY(u,i);
uz[i]=-GRADZ(u,i);
}
}
*/
    /********** Calc Forces of Bana (for Magara-MHD) **************/
    /*
if((calcb==21) || (calcb==11))
{
if((streamw = fopen("Bana.bin","rb")) == NULL) { printf("\n Error Bana.bin"); exit(1);}
fread(B,sizeof(double)*3*nxnynz,1,streamw);
printf("\t Read finished ");

#ifdef _OPENMP
#pragma omp parallel for private (i)
#endif
for(i=0;i<nxnynz;i++)
{
Bxana[i]=B[i];
Byana[i]=B[i+nxnynz];
Bzana[i]=B[i+2*nxnynz];
}

for(ix=0;ix<nx-0;ix++)
for(iy=0;iy<ny-0;iy++)
for(iz=0;iz<nz-0;iz++)
{
i=ix*nynz+iy*nz+iz;
Jx[i]=GRADY(Bzana,i)-GRADZ(Byana,i);
Jy[i]=GRADZ(Bxana,i)-GRADX(Bzana,i);
Jz[i]=GRADX(Byana,i)-GRADY(Bxana,i);

Vx[i]=Jy[i]*Bzana[i]-Jz[i]*Byana[i];
Vy[i]=Jz[i]*Bxana[i]-Jx[i]*Bzana[i];
Vz[i]=Jx[i]*Byana[i]-Jy[i]*Bxana[i];
ux[i]=-Vx[i];
uy[i]=-Vy[i];
uz[i]=-Vz[i];
}
dummy1=dummy2=dummy3=0.0;
for(ix=0;ix<nx-0;ix++)
for(iy=0;iy<ny-0;iy++)
for(iz=0;iz<nz-0;iz++)
{
i=ix*nynz+iy*nz+iz;
dummy1=dummy1+sqrt(ux[i]*ux[i]+uy[i]*uy[i]+uz[i]*uz[i]);
dummy2=dummy2+Bxana[i]*Bxana[i]+Byana[i]*Byana[i]+Bzana[i]*Bzana[i];
dummy3=dummy3+sqrt(Jx[i]*Jx[i]+Jy[i]*Jy[i]+Jz[i]*Jz[i])*
sqrt(Bxana[i]*Bxana[i]+Byana[i]*Byana[i]+Bzana[i]*Bzana[i]);
;
}
printf("\n *** FORCES calculated from Bana F=-JxB ***");
printf("\n|J x B|/|B^2/L|= %lf",Lx*dummy1/dummy2);
printf("\n|J x B|/|J|*|B|= %lf",dummy1/dummy3);
}
*/
    /********** Read weight function wa0+wb0 *************/
    /********** wa for force, wb for div B   *************/

    if (maxit == 987654)
    {
        if ((streamw = fopen("wa.bin", "rb")) == NULL)
        {
            printf("\n Error wa.bin");
            exit(1);
        }
        fread(wa0, sizeof(double) * 1 * nxnynz, 1, streamw);
        printf("\n Read wa finished ");
        if ((streamw = fopen("wb.bin", "rb")) == NULL)
        {
            printf("\n Error wb.bin");
            exit(1);
        }
        fread(wb0, sizeof(double) * 1 * nxnynz, 1, streamw);
        printf("\n Read wb finished ");
    }
    else
    {
        printf("\n Calculate wa and wb ");
#ifdef _OPENMP
#pragma omp parallel for private(i)
#endif
        for (i = 0; i < nxnynz; i++)
        {
            wa0[i] = wb0[i] = 1.0;
        }
        if (nd > 1)
        {
            prof = (float *)calloc(nd, sizeof(float));
            xprof = (float *)calloc(nx, sizeof(float));
            yprof = (float *)calloc(ny, sizeof(float));
            zprof = (float *)calloc(nz, sizeof(float));
            for (i = 0; i < nd; i++)
            {
                prof[i] = 0.5 + 0.5 * cos(1.0 * i / (nd - 1) * 3.14159);
            }
            for (ix = 0; ix < nx; ix++)
            {
                xprof[ix] = 1.0;
            }
            for (iy = 0; iy < ny; iy++)
            {
                yprof[iy] = 1.0;
            }
            for (iz = 0; iz < nz; iz++)
            {
                zprof[iz] = 1.0;
            }
            for (i = 0; i < nd; i++)
            {
                xprof[nx - nd + i] = prof[i];
                xprof[nd - i - 1] = prof[i];
                yprof[ny - nd + i] = prof[i];
                yprof[nd - i - 1] = prof[i];
                zprof[nz - nd + i] = prof[i];
            }
#ifdef _OPENMP
#pragma omp parallel for private(i, ix, iy, iz)
#endif
            for (ix = 0; ix < nx; ix++)
                for (iy = 0; iy < ny; iy++)
                    for (iz = 0; iz < nz; iz++)
                    {
                        i = ix * nynz + iy * nz + iz;
                        wa0[i] = xprof[ix] * yprof[iy] * zprof[iz];
                        wb0[i] = xprof[ix] * yprof[iy] * zprof[iz];
                    }
        }
    }
#ifdef _OPENMP
#pragma omp parallel for private(i)
#endif
    for (i = 0; i < nxnynz; i++)
    {
        wax[i] = GRADX(wa0, i);
        way[i] = GRADY(wa0, i);
        waz[i] = GRADZ(wa0, i);
        wbx[i] = GRADX(wb0, i);
        wby[i] = GRADY(wb0, i);
        wbz[i] = GRADZ(wb0, i);
    }

    nxnynz1 = (nx - 2 * nd) * (ny - 2 * nd) * (nz - nd);
    printf("\n Boundary layer nd= %i ", nd);
    printf("\n Inner region = %.2f", (double)(nxnynz1) / (nxnynz));

    /******************************************************/
    /* for(it=0;it<maxit;it++) */
    it = -1;
    /* while(it<maxit && mue/1.0e11>0.001) */
    mue = 0.1 * dx * dx;

    /* Added 03.08.2011 */
    restore = 0; /* No restore at beginning */
    printf("\n Iteration_start.mark \n");
    if ((streamw = fopen("Iteration_start.mark", "w")) == NULL)
    {
        printf("\n Error mark");
        exit(1);
    }
    fclose(streamw);
    while (it < maxit && statcount < 10 && mue > 1.0e-7 * dx * dx)
    {
        it = it + 1;
        /* printf("\n test= %i",it); */
        /* printf("\n Restprogram zeit= %lf", zeit()); */
        if (calcb != 10)
        {
            L = calculateL();
            if (calcb == 40)
            {
                L3 = 0.0;
                for (ix = 0; ix < nx; ix++)
                    for (iy = 0; iy < ny; iy++)
                    {
                        i = ix * nynz + iy * nz + iz;
                        i1 = ix * ny + iy;
                        L3 = L3 + mask[i1] * ((Bx[i] - Bxorig[i1]) * (Bx[i] - Bxorig[i1]) + (By[i] - Byorig[i1]) * (By[i] - Byorig[i1]) + (Bz[i] - Bzorig[i1]) * (Bz[i] - Bzorig[i1]));
                    }
                /* L3=L3/nx/ny; */
                /* printf("\n nave= %i",nave); */
                L3 = L3 / nave;
                L = L + L3;
            }

            if (it == 0)
            {
                oldL = L;
            }
            if (restore == 1)
            {
                L = oldL;
            }                                      /* restore when L is rejected */
            if (it > 0 && L > oldL && calcb != 41) /* Changed L>=oldL to L>oldL */
            {
                restore = 1; /* restore in the next loop step */
                /* it=it-1;  */
                mue = mue / 2.0;
                printf("\n mue reduced, mue= %lf \t mue/dx^2= %lf", mue, mue / (dx * dx));
                printf("\n oldL= %lf \t L=%lf", oldL, L);
                it = it - 1;
#ifdef _OPENMP
#pragma omp parallel for private(i)
#endif
                for (i = 0; i < nxnynz; i++) /* step too large, refused */
                {
                    Bx[i] = Bx1[i] = Bx2[i];
                    By[i] = By1[i] = By2[i];
                    Bz[i] = Bz1[i] = Bz2[i];
                }
            }
            else
            {
                if (calcb != 41)
                {
                    mue = mue * 1.01;
                }
                restore = 0; /* no restore */
                oldL = L;
            }
            /* oldL=L; */
        }

        if (calcb == 10)
        {
            calculateJxB();
            classicrelax();
        }
        if (calcb != 10 && oldL >= L)
        {
            /*** L minimieren ***/
            nu = 0.1e12;
#ifdef _OPENMP
#pragma omp parallel for private(i, ix, iy, iz)
#endif
            for (ix = 1; ix < nx - 1; ix++)
                for (iy = 1; iy < ny - 1; iy++)
                    for (iz = 1; iz < nz - 1; iz++)
                    {
                        i = ix * nynz + iy * nz + iz;
                        Bx1[i] = Bx[i] + 1.0 * mue * Fx[i];
                        By1[i] = By[i] + 1.0 * mue * Fy[i];
                        Bz1[i] = Bz[i] + 1.0 * mue * Fz[i];
                    }
            /*  Try to repair errors in Magnetogram */
            if (calcb == 40)
            {
                iz = 0;
                mue2 = mue;

                for (ix = 0; ix < nx; ix++)
                    for (iy = 0; iy < ny; iy++)
                    {
                        i = ix * nynz + iy * nz + iz;
                        i1 = ix * ny + iy;
                        Bx1[i] = Bx[i] - 1.0 * mue2 * oxby[i] - nue * mask[i1] * (Bx[i] - Bxorig[i1]);
                        By1[i] = By[i] + 1.0 * mue2 * oxbx[i] - nue * mask[i1] * (By[i] - Byorig[i1]);
                        Bz1[i] = Bz[i] - nue * (Bz[i] - Bzorig[i1]);
                    }
            }

            /* Use G to minmize L at the boundary */
            /* if(it%1==0 && it !=0 &&1==2 &&it <500000 )
*/
            if ((calcb == 40) && (boundary == 1))
            {
                mue2 = mue / (1.0 * Lx) / 50.0;
                mue2 = mue;
                /* printf("\n Boundary-Relax "); */
                for (ix = 0; ix < nx - 0; ix++)
                    for (iy = 0; iy < ny - 0; iy++)
                    {
                        iz = 0; /* bottom */
                        i = ix * nynz + iy * nz + iz;
                        /*
if(Bz[i]<100000000.0)
{
Bx1[i]=Bx[i]-1.0*mue2*oxby[i];
By1[i]=By[i]+1.0*mue2*oxbx[i];
Bz1[i]=Bz[i]-1.0*mue2*odotb[i];
}
*/
                        iz = nz - 1; /*top */
                        i = ix * nynz + iy * nz + iz;
                        Bx1[i] = Bx[i] + mue2 * oxby[i];
                        By1[i] = By[i] - mue2 * oxbx[i];
                        Bz1[i] = 1.0 * (Bz[i] + mue2 * odotb[i]);
                    }
                for (ix = 0; ix < nx - 0; ix++)
                    for (iz = 0; iz < nz - 0; iz++)
                    {
                        iy = 0; /* front */
                        i = ix * nynz + iy * nz + iz;
                        Bx1[i] = Bx[i] + mue2 * oxbz[i];
                        By1[i] = 1.0 * (By[i] - mue2 * odotb[i]);
                        Bz1[i] = Bz[i] - mue2 * oxbx[i];
                        iy = ny - 1; /* back */
                        i = ix * nynz + iy * nz + iz;
                        Bx1[i] = Bx[i] - mue2 * oxbz[i];
                        By1[i] = 1.0 * (By[i] + mue2 * odotb[i]);
                        Bz1[i] = Bz[i] + mue2 * oxbx[i];
                    }
                for (iy = 0; iy < ny - 0; iy++)
                    for (iz = 0; iz < nz - 0; iz++)
                    {
                        ix = 0; /* left */
                        i = ix * nynz + iy * nz + iz;
                        Bx1[i] = 1.0 * (Bx[i] - mue2 * odotb[i]);
                        By1[i] = By[i] - mue2 * oxbz[i];
                        Bz1[i] = Bz[i] + mue2 * oxby[i];
                        ix = nx - 1; /* right */
                        i = ix * nynz + iy * nz + iz;
                        Bx1[i] = 1.0 * (Bx[i] + mue2 * odotb[i]);
                        By1[i] = By[i] + mue2 * oxbz[i];
                        Bz1[i] = Bz[i] - mue2 * oxby[i];
                    }
            }
        }

        /*** Some tests with (Anti) Symmetric Boundary-conditions ***/

        /***********************************************************/
        diagstep = 10;

        if (it % diagstep == 0) /* && L<=oldL ) */
        {
            /************************************************************/
            /************ Diagnostics ***********************************/
            /************************************************************/
            /*
    calculateJxB();
totB=divB=divJ=totJ=totV=0.0;
maxdivB=maxB=maxJ=minJ=maxV=0.0;
#ifdef _OPENMP
#pragma omp parallel for private (i,ix,iy,iz,dummy)  reduction(+:totB) reduction(+:divB) reduction(+:totJ) reduction(+:totV)
#endif
for(ix=nd;ix<nx-nd;ix++)
for(iy=nd;iy<ny-nd;iy++)
for(iz=0;iz<nz-nd;iz++)
{
i=nynz*ix+nz*iy+iz;
dummy=sqrt(Bx[i]*Bx[i]+By[i]*By[i]+Bz[i]*Bz[i]);
totB=totB+dummy;
dummy=fabs(GRADX(Bx,i)+GRADY(By,i)+GRADZ(Bz,i));
divB=divB+dummy;
dummy=sqrt(Jx[i]*Jx[i]+Jy[i]*Jy[i]+Jz[i]*Jz[i]);
totJ=totJ+dummy;
dummy=sqrt(Vx[i]*Vx[i]+Vy[i]*Vy[i]+Vz[i]*Vz[i]);
totV=totV+dummy;
}
totB=totB/nxnynz1;


divB=divB/nxnynz1;
totJ=totJ/nxnynz1;
divJ=divJ/nxnynz1;
totV=totV/nxnynz1;
*/

            time1 = zeit();
            if (time1 > 0.0)
            {
                timetot = timetot + time1;
            }
            if (calcb == 10)
            {
                L = calculateL();
            }
            Li = calculateLi();

            /* printf("\n %i L= %.4f, L_i= %.4f, |J x B| = %.2f, cpu %.1f s", it,L,Li,totV,time1);
printf("\n %i L= %.4f, L_i= %.4f,  cpu %.1f s", it,L,Li,time1); */
            printf("\n %i L= %.4f, L_i= %.4f", it, L, Li);
            dummy = 0.0;
            dummy1 = dummy2 = 0.0;
            /* NEW: calc gradient (dL/dt)L for stopping rule */
            if (it == 0)
            {
                prevL = 2.0 * L;
                newL = L;
            }
            else
            {
                prevL = newL;
                newL = L;
            }
            gradL = fabs((newL - prevL) / newL);
            if (gradL < 0.0001)
            {
                statcount = statcount + 1;
                printf("\n *** STATIONARY STATE count: %i *** grad L/L= %lf \n", statcount, gradL);
            }
            if (gradL > 0.0001)
            {
                statcount = 0;
            }
            /*
#ifdef _OPENMP
#pragma omp parallel for private (i,ix,iy,iz) reduction(+:dummy1,+:dummy2)
#endif
for(ix=nd;ix<nx-nd;ix++)
for(iy=nd;iy<ny-nd;iy++)
for(iz=0;iz<nz-nd;iz++)
{
i=ix*nynz+iy*nz+iz;
dummy2=dummy2+Bxana[i]*Bxana[i]+Byana[i]*Byana[i]+Bzana[i]*Bzana[i];
dummy1=dummy1+(Bx[i]-Bxana[i])*(Bx[i]-Bxana[i])+(By[i]-Byana[i])*(By[i]-Byana[i])+(Bz[i]-Bzana[i])*(Bz[i]-Bzana[i]);

}
*/
            dummy1 = 0.0;
            dummy2 = 1.0;
            dummy = sqrt(dummy1 / dummy2);
            if (calcb != 40)
                printf(",  gradL/L= %lf", gradL);
            if (calcb == 40)
            {
                printf(",L1=%.4lf, L2=%.4lf,  L3= %.4lf", L1, L2, L3);
            }
            if ((streamw = fopen("step.log", "w")) == NULL)
            {
                printf("\n Error help.log");
                exit(1);
            }
            fprintf(streamw, "%i", it / diagstep);
            fclose(streamw);
            if ((streamw = fopen("prot.log", "a")) == NULL)
            {
                printf("\n Error prot.log");
                exit(1);
            }
            /* fprintf(streamw,"%lf \n %lf \n %lf \n %lf \n %lf \n %lf \n", 1.0*it,L,Li,totV,divB,gradL);*/
            fprintf(streamw, "%lf \n %lf \n %lf \n %lf \n %lf \n %lf \n %lf \n", 1.0 * it, L, Li, gradL, L1, L2, L3);
            fclose(streamw);
        }
/* End Diagnostik */
#ifdef _OPENMP
#pragma omp parallel for private(i)
#endif
        for (i = 0; i < nxnynz; i++)
        {
            Bx2[i] = Bx[i];
            By2[i] = By[i];
            Bz2[i] = Bz[i];
        }
#ifdef _OPENMP
#pragma omp parallel for private(i)
#endif
        for (i = 0; i < nxnynz; i++)
        {
            Bx[i] = Bx1[i];
            By[i] = By1[i];
            Bz[i] = Bz1[i];
        }
    }
    if (calcb == 15)
    {
        printf("\n\n ********** Final Boundary : old= %lf \t new= %lf \t********\n", w2, 1.0 - w2);
    }

    /******* Binary Output *******************/
    /*
#ifdef _OPENMP
#pragma omp parallel for private (i)
#endif
for(i=0;i<nxnynz;i++)
{
i2=i+nxnynz;
i3=i2+nxnynz;
B[i]=Bx[i];
B[i2]=By[i];
B[i3]=Bz[i];
}
*/
    printf("\n Iteration_stop.mark \n");
    if ((streamw = fopen("Iteration_stop.mark", "w")) == NULL)
    {
        printf("\n Error mark");
        exit(1);
    }
    fclose(streamw);
    if (1 == 1) /* norm B, only inner Region */
    {
#ifdef _OPENMP
#pragma omp parallel for private(i)
#endif
        for (i = 0; i < nxnynz; i++)
        {
            Bx[i] = Bx[i] * Bave;
            By[i] = By[i] * Bave;
            Bz[i] = Bz[i] * Bave;
        }
    }

    if ((streamw = fopen("Bout.bin", "wb")) == NULL)
    {
        printf("\n Error Bout.bin");
        exit(1);
    }
    /* fwrite(B,sizeof(double)*3*nxnynz,1,streamw); */
    fwrite(Bx, sizeof(double) * nxnynz, 1, streamw);
    fwrite(By, sizeof(double) * nxnynz, 1, streamw);
    fwrite(Bz, sizeof(double) * nxnynz, 1, streamw);
    fclose(streamw);
    printf("\n\n Relaxed B written to Bout.bin done ");

    /******* ASCII Output *******************/
    /*
if((streamw = fopen("Bout.dat","w")) == NULL) { printf("\n Error Bout.dat"); exit(1);}


for(iz=0;iz<nz-1;iz++)
for(iy=0;iy<ny-1;iy++)
for(ix=0;ix<nx-1;ix++)
{
i=nynz*ix+nz*iy+iz;
fprintf(streamw,"%lf\n %lf\n%lf\n",Bx[i],By[i],Bz[i]);
}
fclose(streamw);
printf("\n\n Relaxed B written to Bout.dat done ");

*/

    printf("\n\n\n End of Program \n\n");
    exit(0);
}
