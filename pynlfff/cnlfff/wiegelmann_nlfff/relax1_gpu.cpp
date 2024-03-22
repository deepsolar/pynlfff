/*
 * @Description: https://doi.org/10.1007/s11207-012-9966-z
 * @Author: Thomas Wiegelmann (wiegelmann@mps.mpg.de)
 * @Date: 
 * @LastEditors: Xinze Zhang (zhangxinze17@mails.ucas.ac.cn)
 * @LastEditDescription: Update GPU version
 * @LastEditTime: 202212
*/

/* relax1.c */
#include <stdio.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>

#define MCENTERGRAD(f, id) ((f[i + id] - f[i - id]) / (2 * h))
#define MLEFTGRAD(f, id) ((-3 * f[i] + 4 * f[i + id] - f[i + 2 * id]) / (2 * h))
#define MRIGHTGRAD(f, id) ((+3 * f[i] - 4 * f[i - id] + f[i - 2 * id]) / (2 * h))

/* GRAD for Boundaries , all 3 differences needed */
#define GRADX(f, i) ((ix > 0 && ix < nx - 1) ? (MCENTERGRAD(f, nynz)) : ((ix == 0) ? (MLEFTGRAD(f, nynz)) : ((ix == nx - 1) ? (MRIGHTGRAD(f, nynz)) : (0.0))))
#define GRADY(f, i) ((iy > 0 && iy < ny - 1) ? (MCENTERGRAD(f, nz)) : ((iy == 0) ? (MLEFTGRAD(f, nz)) : ((iy == ny - 1) ? (MRIGHTGRAD(f, nz)) : (0.0))))
#define GRADZ(f, i) ((iz > 0 && iz < nz - 1) ? (MCENTERGRAD(f, 1)) : ((iz == 0) ? (MLEFTGRAD(f, 1)) : ((iz == nz - 1) ? (MRIGHTGRAD(f, 1)) : (0.0))))

FILE *streamw, *initfile;

void green(double *Bx, double *By, double *Bz);

void calculate(const int maxit, const int diagstep, const int calcb, const int boundary, const int nx, const int ny, const int nz, const double dx, const double dy, const double dz, const double Lx, const double nave, const double nue,
               const double *Bxorig, const double *Byorig, const double *Bzorig, const double *mask,
               int &it, double &mue, FILE *streamw, double *Bx, double *By, double *Bz);

void loadvectormag2(const int nx, const int ny, double *Bxorig, double *Byorig, double *Bzorig)
{
    int ix, iy, iz, i;
    double dummy;
    if ((streamw = fopen("allboundaries.dat", "r")) == NULL)
    {
        printf("\n Error ");
        exit(1);
    }
    iz = 0;
    for (iy = 0; iy < ny; iy++)
        for (ix = 0; ix < nx; ix++)
        {
            i = ny * ix + iy;
            fscanf(streamw, "%lf", &dummy);
            Bxorig[i] = dummy;
            fscanf(streamw, "%lf", &dummy);
            Byorig[i] = dummy;
            fscanf(streamw, "%lf", &dummy);
            Bzorig[i] = dummy;
        }
    fclose(streamw);
    printf("\n Vectormagnetogram loaded in Bobs\n");
}

/****************************************************/
/******* MAIN PROGRAM   *****************************/
/****************************************************/

double time1_calculate, time2_calculate, timeTot_calculate;
double time1_calculate1, time2_calculate1, timeTot_calculate1;
double time1_calculate2, time2_calculate2, timeTot_calculate2;
double time1_calculate3, time2_calculate3, timeTot_calculate3;
double time1_calculate4, time2_calculate4, timeTot_calculate4;

int main(int argc, char *argv[])
{
    double Lx, Ly, Lz, alpha, pi, q1;
    double *t, *xt, *yt, *zt, *absB, *t2, *xyzB, *refB;
    double *x, *y, *z;
    double *Bx, *By, *Bz;
    float *VxBx, *VxBy, *VxBz, *Rotvx, *Rotvy, *Rotvz;
    float *Jx, *Jy, *Jz, *Vx, *Vy, *Vz;
    float *Jx1, *Jy1, *Jz1;
    float *ox, *oy, *oz;
    double *Bxorig, *Byorig, *Bzorig, *mask;
    double dt, length;
    double C;
    double dx, dy, dz, h;
    double mu0, rmu0, Ls, gausT, rmu0gausT, mue;
    double Bave, Lxyave;
    int maxsteps, max2;
    int nx, ny, nz, nynz, nxnynz, nd, nxmax, nymax, nzmax;
    int calcb, maxit, firsttime, m0, n0;
    int nxnynz1, nxnynz2, diagstep;

    int i, i1, it, ix, iy, iz;
    double dummy;
    double time1, time2, timeTot;
    double nave;
    double w2, w, Llimit;
    double nue;
    int boundary;

    float *prof, *xprof, *yprof, *zprof;
    char leer[25];
    w2 = w = Llimit = 0.0;

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

    time1 = clock();
    timeTot_calculate = 0;
    timeTot_calculate1 = 0;
    timeTot_calculate2 = 0;
    timeTot_calculate3 = 0;
    diagstep = 10;
    q1 = 1.0;
    mu0 = 1.2566e-6;
    rmu0 = 1. / mu0;
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
    printf("\n nx= %i, ny=%i , nz= %i \n", nx, ny, nz);

    nynz = ny * nz;
    nxnynz = nx * ny * nz;
    nxnynz1 = (nx - 0) * (ny - 0) * (nz - 0);
    nxnynz2 = (nx - 0) * (ny - 0) * (nz - 0);
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
    printf("\n\n Size of double: %i", sizeof(double));
    printf("\n nxnynz * Size of double: %i", nxnynz * sizeof(double));
    printf("\n nxnynz * Size of float: %i", nxnynz * sizeof(float));

    /*********************************************************/
    ox = (float *)calloc(nxnynz, sizeof(float));
    oy = (float *)calloc(nxnynz, sizeof(float));
    oz = (float *)calloc(nxnynz, sizeof(float));

    /*************************************************************************************/
    if (calcb == 23)
    {
        printf("\n Computing Potential field \n");
        green(Bx, By, Bz);
        exit(1);
    }

    if ((streamw = fopen("prot.log", "w")) == NULL)
    {
        printf("\n Error prot.log");
        exit(1);
    }
    fclose(streamw);
    alpha = 0.0;

    printf("\n\n alpha = %lf", alpha);

    nxmax = nx;
    nymax = ny;
    nzmax = nz;

    for (i = 0; i < nxnynz; i++)
    {
        ox[i] = oy[i] = oz[i] = 0.0;
    }

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

    printf("\n Lx= %lf \t Ly= %lf \t Lz= %lf", Lx, Ly, Lz);
    printf("\n nx= %i \t ny= %i \t nz= %i", nx, ny, nz);
    dx = dy = dz = Lx / (nx - 1); /* (nxmax-1); */

    printf("\n\n Lx = %.2lf \t Ly= %.2lf \t Lz= %.2lf ", Lx, Ly, Lz);
    printf("\n dx = %.5lf \t dy= %.5lf \t dz= %.5lf \n\n", dx, dy, dz);
    /************************************************************************************/

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

        loadvectormag2(nx, ny, Bxorig, Byorig, Bzorig);

        if ((streamw = fopen("mask.dat", "r")) == NULL)
        {
            printf("\n Error mask.dat");
            exit(1);
        }
        for (iy = 0; iy < ny; iy++)
            for (ix = 0; ix < nx; ix++)
            {
                i1 = ny * ix + iy;
                fscanf(streamw, "%lf", &dummy);
                mask[i1] = dummy;
            }
        fclose(streamw);
        nue = 1.0;
        boundary = 0;
        if ((initfile = fopen("boundary.ini", "r")) == NULL)
        {
            printf("\n No File boundary.ini ");
            printf("\n Use default values:");
        }
        else
        {
            printf("\n boundary.ini exists \n");
            fscanf(initfile, "%s %lf", &leer, &nue);
            fscanf(initfile, "%s %i", &leer, &boundary);
            fclose(initfile);
            printf("\n nue= %lf, \t boundary= %i", nue, boundary);
        }
    }

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

    printf("\n nx= %i, ny=%i, nz=%i, nynz=%i, nxnynz=%i \n", nx, ny, nz, nynz, nxnynz);

    /**************************************************************************************/
    /************************ Relaxation   Loop                ****************************/
    /**************************************************************************************/
    /* maxit=51; */
    printf("\n calcb= %i", calcb);
    printf("\n maxit= %i", maxit);
    h = dx;

    /********** Calc Forces of Bana (for Magara-MHD) **************/

    /********** wa for force, wb for div B   *************/

    printf("\n Calculate wa and wb ");

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
    }

    nxnynz1 = (nx - 2 * nd) * (ny - 2 * nd) * (nz - nd);
    printf("\n Boundary layer nd= %i ", nd);
    printf("\n Inner region = %.2f", (double)(nxnynz1) / (nxnynz));

    /******************************************************/
    it = -1;
    mue = 0.1 * dx * dx;

    /* Added 03.08.2011 */
    printf("\n Iteration_start.mark \n");
    if ((streamw = fopen("Iteration_start.mark", "w")) == NULL)
    {
        printf("\n Error mark");
        exit(1);
    }
    fclose(streamw);

    calculate(maxit, diagstep, calcb, boundary, nx, ny, nz, dx, dy, dz, Lx, nave, nue, Bxorig, Byorig, Bzorig, mask, it, mue, streamw, Bx, By, Bz);

    /******* Binary Output *******************/

    printf("\n Iteration_stop.mark \n");
    if ((streamw = fopen("Iteration_stop.mark", "w")) == NULL)
    {
        printf("\n Error mark");
        exit(1);
    }
    fclose(streamw);
    if (1 == 1) /* norm B, only inner Region */
    {
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

    fwrite(Bx, sizeof(double) * nxnynz, 1, streamw);
    fwrite(By, sizeof(double) * nxnynz, 1, streamw);
    fwrite(Bz, sizeof(double) * nxnynz, 1, streamw);
    fclose(streamw);
    printf("\n\n Relaxed B written to Bout.bin done ");

    /******* ASCII Output *******************/

    time2 = clock();
    timeTot = (time2 - time1) / CLOCKS_PER_SEC;
    printf("\n\n\n End of Program\nTime: %f %f %f\n\t%f %f %f %f \n \n\n", timeTot_calculate, timeTot, 100 * timeTot_calculate / timeTot, timeTot_calculate1, timeTot_calculate2, timeTot_calculate3, timeTot_calculate4);
    exit(0);
}
