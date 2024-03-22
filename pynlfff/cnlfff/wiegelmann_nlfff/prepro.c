/*
 * @Description: https://doi.org/10.1007/s11207-012-9966-z
 * @Author: Thomas Wiegelmann (wiegelmann@mps.mpg.de)
 * @Date: 
 * @LastEditors: Thomas Wiegelmann (wiegelmann@mps.mpg.de)
 * @LastEditTime: 
*/

/* prepro.c */
#include <stdio.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#define DOUBLE double

main(int argc, char *argv[])
{
    FILE *streamw, *initfile;
    double *x, *y, *r;
    double *Bx, *By, *Bz;
    double *Bxold, *Byold, *Bzold;
    double *Bxo, *Byo, *Bzo;
    double *Bx1, *By1, *Bz1;
    double *Hx, *Hy, *w;
    double *LapBx, *LapBy, *LapBz;
    double *term3a, *term3b, *term3c;
    double *term4a, *term4b, *term4c;
    char leer[5];
    double dummy1, Bave, fac1, dt, dt0;
    double mu1, mu2, mu3, mu4, mu5;
    double dx, dy, dxdy;
    double Emag, Emag2, ihelp, ihelp2;
    double dL, L, L1, L2, L12, L3, L4, L5;
    double oldL12, oldL3, oldL4, oldL5, oldL;
    double dL12, dL3, dL4, dL5;
    double term1a, term1b, term1c, term1c1, term1c2;
    double term2a, term2b, term2c;
    double term2a1, term2a2, term2b1, term2b2, term2c1, term2c2;
    double term5;
    double Lvec[5];
    int nx, ny, nxny;
    int i, ix, iy, it;
    int i1, i2, ix1, iy1;
    int i3, i4, ix2, iy2;

    mu1 = mu2 = 1.0;
    mu3 = 0.001;
    mu4 = 0.01;
    mu5 = 0.0;
    if (argc < 2)
    {
        printf("mu3 not given! Use default");
    }
    else
    {
        if (!sscanf(argv[1], "%lf", &mu3))
        {
            printf("\n Something wrong with mu3 \n");
            exit(1);
        }
    }
    if (argc < 3)
    {
        printf("mu4 not given! Use default");
    }
    else
    {
        if (!sscanf(argv[2], "%lf", &mu4))
        {
            printf("\n Something wrong with mu4 \n");
            exit(1);
        }
    }

    if (argc > 3)
        if (!sscanf(argv[3], "%lf", &mu5))
        {
            printf("\n Something wrong with mu5 \n");
            exit(1);
        }

    printf("\n mu3= %lf \t mu4= %lf \t mu5= %lf", mu3, mu4, mu5);

    if ((initfile = fopen("grid.ini", "r")) == NULL)
    {
        printf("\n Error grid.ini");
        exit(1);
    }
    fscanf(initfile, "%s %i", &leer, &nx);
    fscanf(initfile, "%s %i", &leer, &ny);
    fclose(initfile);
    nxny = nx * ny;
    printf("\n nx= %i, ny=%i, nxny=%i  \n", nx, ny, nxny);

    Bx = (DOUBLE *)calloc(nxny, sizeof(DOUBLE));
    By = (DOUBLE *)calloc(nxny, sizeof(DOUBLE));
    Bz = (DOUBLE *)calloc(nxny, sizeof(DOUBLE));
    LapBx = (DOUBLE *)calloc(nxny, sizeof(DOUBLE));
    LapBy = (DOUBLE *)calloc(nxny, sizeof(DOUBLE));
    LapBz = (DOUBLE *)calloc(nxny, sizeof(DOUBLE));
    Bx1 = (DOUBLE *)calloc(nxny, sizeof(DOUBLE));
    By1 = (DOUBLE *)calloc(nxny, sizeof(DOUBLE));
    Bz1 = (DOUBLE *)calloc(nxny, sizeof(DOUBLE));
    Bxo = (DOUBLE *)calloc(nxny, sizeof(DOUBLE));
    Byo = (DOUBLE *)calloc(nxny, sizeof(DOUBLE));
    Bzo = (DOUBLE *)calloc(nxny, sizeof(DOUBLE));
    Bxold = (DOUBLE *)calloc(nxny, sizeof(DOUBLE));
    Byold = (DOUBLE *)calloc(nxny, sizeof(DOUBLE));
    Bzold = (DOUBLE *)calloc(nxny, sizeof(DOUBLE));
    x = (DOUBLE *)calloc(nx, sizeof(DOUBLE));
    y = (DOUBLE *)calloc(ny, sizeof(DOUBLE));
    r = (DOUBLE *)calloc(nxny, sizeof(DOUBLE));
    term3a = (DOUBLE *)calloc(nxny, sizeof(DOUBLE));
    term3b = (DOUBLE *)calloc(nxny, sizeof(DOUBLE));
    term3c = (DOUBLE *)calloc(nxny, sizeof(DOUBLE));
    term4a = (DOUBLE *)calloc(nxny, sizeof(DOUBLE));
    term4b = (DOUBLE *)calloc(nxny, sizeof(DOUBLE));
    term4c = (DOUBLE *)calloc(nxny, sizeof(DOUBLE));

    if (mu5 != 0.0)
    {
        printf("\n Using Halpha images for preprocessing");
        Hx = (DOUBLE *)calloc(nxny, sizeof(DOUBLE));
        Hy = (DOUBLE *)calloc(nxny, sizeof(DOUBLE));
        w = (DOUBLE *)calloc(nxny, sizeof(DOUBLE));
        if ((streamw = fopen("halpha.dat", "r")) == NULL)
        {
            printf("\n Error halpha.dat ");
            exit(1);
        }
        for (iy = 0; iy < ny; iy++)
            for (ix = 0; ix < nx; ix++)
            {
                i = ny * ix + iy;
                fscanf(streamw, "%lf", &dummy1);
                Hx[i] = dummy1;
                fscanf(streamw, "%lf", &dummy1);
                Hy[i] = dummy1;
            }
        fclose(streamw);
        printf("\n Halpha image (Hx,Hy) halpha.dat loaded ");
        if ((streamw = fopen("w.dat", "r")) == NULL)
        {
            printf("\n Error w.dat ");
            exit(1);
        }
        for (iy = 0; iy < ny; iy++)
            for (ix = 0; ix < nx; ix++)
            {
                i = ny * ix + iy;
                fscanf(streamw, "%lf", &dummy1);
                w[i] = dummy1;
            }
        fclose(streamw);
        printf("\n weighting function w.dat loaded ");
    }
    if ((streamw = fopen("input.dat", "r")) == NULL)
    {
        printf("\n Error input.dat ");
        exit(1);
    }
    for (iy = 0; iy < ny; iy++)
        for (ix = 0; ix < nx; ix++)
        {
            i = ny * ix + iy;
            fscanf(streamw, "%lf", &dummy1);
            Bx[i] = dummy1;
            fscanf(streamw, "%lf", &dummy1);
            By[i] = dummy1;
            fscanf(streamw, "%lf", &dummy1);
            Bz[i] = dummy1;
        }
    fclose(streamw);
    printf("\n Vectormagnetogram input.dat loaded \n");
    Bave = 0.0;
#ifdef _OPENMP
#pragma omp parallel for private(i, ix, iy) reduction(+ \
                                                      : Bave)
#endif
    for (ix = 0; ix < nx; ix++)
        for (iy = 0; iy < ny; iy++)
        {
            i = ny * ix + iy;
            Bave = Bave + sqrt(Bx[i] * Bx[i] + By[i] * By[i] + Bz[i] * Bz[i]);
        }
    Bave = Bave / nx / ny;
    printf("\n Bave= %lf", Bave);

#ifdef _OPENMP
#pragma omp parallel for private(i)
#endif
    for (i = 0; i < nxny; i++)
    {
        Bx[i] = Bx1[i] = Bxo[i] = Bxold[i] = Bx[i] / Bave;
        By[i] = By1[i] = Byo[i] = Byold[i] = By[i] / Bave;
        Bz[i] = Bz1[i] = Bzo[i] = Bzold[i] = Bz[i] / Bave;
    }
    dx = 1.0 / (nx - 1);
    dy = 1.0 / (ny - 1);
    dxdy = dx * dy;
    for (ix = 0; ix < nx; ix++)
    {
        x[ix] = ix * dx;
    }
    for (iy = 0; iy < ny; iy++)
    {
        y[iy] = iy * dy;
    }
#ifdef _OPENMP
#pragma omp parallel for private(i, ix, iy)
#endif
    for (ix = 0; ix < nx; ix++)
        for (iy = 0; iy < ny; iy++)
        {
            i = ny * ix + iy;
            r[i] = sqrt(x[ix] * x[ix] + y[iy] * y[iy]);
        }
    /* Do the Preprocessing */
    fac1 = 10.0;
    dt = 0.1;
    /*
mu1=mu1/fac1; mu2=mu2/fac1; mu3=mu3/fac1;
mu4=mu4/fac1; mu5=mu5/fac1;
*/
    Emag = ihelp = 0.0;
#ifdef _OPENMP
#pragma omp parallel for private(i) reduction(+                   \
                                              : Emag) reduction(+ \
                                                                : ihelp)
#endif
    for (i = 0; i < nxny; i++)
    {
        Emag = Emag + Bx[i] * Bx[i] + By[i] * By[i] + Bz[i] * Bz[i];
        ihelp = ihelp + r[i] * (Bx[i] * Bx[i] + By[i] * By[i] + Bz[i] * Bz[i]);
    }
    printf("\n Emag= %lf, ihelp= %lf", Emag, ihelp);
    L = 10.0;
    dL = 1.0;
    oldL = 10.0;
    it = -1;
    printf("\n L12, L3, L4 are multiplied with 1.0e6");
    /*************************************/
    /********** Start Iteration **********/
    /*************************************/

    /* Now some experiments with timestep */
    /* for(it=1;it<5;it++)*/
    while (it < 10000 && dL > 0.0001 && dt > 1.0e-6)
    {
        it = it + 1;

        term1a = term1b = term1c = term1c1 = term1c2 = 0.0;
        term2a = term2b = term2c = 0.0;
        term2a1 = term2b1 = term2c1 = 0.0;
        term2a2 = term2b2 = term2c2 = 0.0;
        L1 = L2 = L3 = L4 = L5 = 0.0;
#ifdef _OPENMP
#pragma omp parallel for private(i, ix, iy) reduction(+                                                                                                                                                                                                                 \
                                                      : term1a) reduction(+                                                                                                                                                                                             \
                                                                          : term1b) reduction(+                                                                                                                                                                         \
                                                                                              : term1c1) reduction(+                                                                                                                                                    \
                                                                                                                   : term1c2) reduction(+                                                                                                                               \
                                                                                                                                        : term2a1) reduction(+                                                                                                          \
                                                                                                                                                             : term2a2) reduction(+                                                                                     \
                                                                                                                                                                                  : term2b1) reduction(+                                                                \
                                                                                                                                                                                                       : term2b2) reduction(+                                           \
                                                                                                                                                                                                                            : term2c1) reduction(+                      \
                                                                                                                                                                                                                                                 : term2c2) reduction(+ \
                                                                                                                                                                                                                                                                      : L3)
#endif
        for (ix = 0; ix < nx; ix++)
            for (iy = 0; iy < ny; iy++)
            {
                i = ny * ix + iy;
                /********** Term 1 Force **********/
                term1a = term1a + Bx[i] * Bz[i];
                term1b = term1b + By[i] * Bz[i];
                term1c1 = term1c1 + Bz[i] * Bz[i];
                term1c2 = term1c2 + Bx[i] * Bx[i] + By[i] * By[i];
                /********** Term 2 Torque **********/
                term2a1 = term2a1 + x[ix] * Bz[i] * Bz[i];
                term2a2 = term2a2 + x[ix] * (Bx[i] * Bx[i] + By[i] * By[i]);
                term2b1 = term2b1 + y[iy] * Bz[i] * Bz[i];
                term2b2 = term2b2 + y[iy] * (Bx[i] * Bx[i] + By[i] * By[i]);
                term2c1 = term2c1 + y[iy] * Bx[i] * Bz[i];
                term2c2 = term2c2 + x[ix] * By[i] * Bz[i];
                /********** Term 3 Data **********/
                term3a[i] = (Bx[i] - Bxo[i]) * (Bx[i] - Bxo[i]) / Emag;
                term3b[i] = (By[i] - Byo[i]) * (By[i] - Byo[i]) / Emag;
                term3c[i] = (Bz[i] - Bzo[i]) * (Bz[i] - Bzo[i]) / Emag;
                L3 = L3 + term3a[i] + term3b[i] + term3c[i];
            }
        term1a = term1a / Emag;
        term1b = term1b / Emag;
        term1c = (term1c1 - term1c2) / Emag;
        term2a = (term2a1 - term2a2) / ihelp;
        term2b = (term2b1 - term2b2) / ihelp;
        term2c = (term2c1 - term2c2) / ihelp;
        L1 = term1a * term1a + term1b * term1b + term1c * term1c;
        L2 = term2a * term2a + term2b * term2b + term2c * term2c;
        L12 = L1 + L2;
        L3 = L3 / Emag;
/********** Laplace Bx,By,Bz **********/
#ifdef _OPENMP
#pragma omp parallel for private(i, ix, iy, ix1, ix2, iy1, iy2, i1, i2, i3, i4) reduction(+ \
                                                                                          : L4)
#endif
        for (ix = 0; ix < nx; ix++)
            for (iy = 0; iy < ny; iy++)
            {
                i = ny * ix + iy;
                ix1 = ix + 1;
                if (ix1 == nx)
                {
                    ix1 = 0;
                }
                ix2 = ix - 1;
                if (ix2 == -1)
                {
                    ix2 = nx - 1;
                }
                iy1 = iy + 1;
                if (iy1 == ny)
                {
                    iy1 = 0;
                }
                iy2 = iy - 1;
                if (iy2 == -1)
                {
                    iy2 = ny - 1;
                }
                i1 = ny * ix1 + iy;
                i2 = ny * ix2 + iy;
                i3 = ny * ix + iy1;
                i4 = ny * ix + iy2;
                LapBx[i] = -4 * Bx[i] + Bx[i1] + Bx[i2] + Bx[i3] + Bx[i4];
                LapBy[i] = -4 * By[i] + By[i1] + By[i2] + By[i3] + By[i4];
                LapBz[i] = -4 * Bz[i] + Bz[i1] + Bz[i2] + Bz[i3] + Bz[i4];
                L4 = L4 + LapBx[i] * LapBx[i] + LapBy[i] * LapBy[i] + LapBz[i] * LapBz[i];
            }
        L4 = dxdy * L4 / Emag;
        L = L1 + L2 + L3 + L4 + L5;
        L = mu1 * L1 + mu2 * L2 + mu3 * L3 + mu4 * L4 + mu5 * L5;
/********** Term 4 Smoothing **********/
#ifdef _OPENMP
#pragma omp parallel for private(i, ix, iy, ix1, ix2, iy1, iy2, i1, i2, i3, i4)
#endif
        for (ix = 0; ix < nx; ix++)
            for (iy = 0; iy < ny; iy++)
            {
                i = ny * ix + iy;
                ix1 = ix + 1;
                if (ix1 == nx)
                {
                    ix1 = 0;
                }
                ix2 = ix - 1;
                if (ix2 == -1)
                {
                    ix2 = nx - 1;
                }
                iy1 = iy + 1;
                if (iy1 == ny)
                {
                    iy1 = 0;
                }
                iy2 = iy - 1;
                if (iy2 == -1)
                {
                    iy2 = ny - 1;
                }
                i1 = ny * ix1 + iy;
                i2 = ny * ix2 + iy;
                i3 = ny * ix + iy1;
                i4 = ny * ix + iy2;
                term4a[i] = -8 * LapBx[i] + 2 * LapBx[i1] + 2 * LapBx[i2] + 2 * LapBx[i3] + 2 * LapBx[i4];
                term4b[i] = -8 * LapBy[i] + 2 * LapBy[i1] + 2 * LapBy[i2] + 2 * LapBy[i3] + 2 * LapBy[i4];
                term4c[i] = -8 * LapBz[i] + 2 * LapBz[i1] + 2 * LapBz[i2] + 2 * LapBz[i3] + 2 * LapBz[i4];
            }
        if (it > 0)
        {
            dL12 = dL3 = dL4 = dL5 = 0.0;
            if (L12 != 0.0)
            {
                dL12 = fabs(L12 - oldL12) / L12;
            }
            if (L3 != 0.0)
            {
                dL3 = fabs(L3 - oldL3) / L3;
            }
            if (L4 != 0.0)
            {
                dL4 = fabs(L4 - oldL4) / L4;
            }
            if (L5 != 0.0)
            {
                dL5 = fabs(L5 - oldL5) / L5;
            }
            /* dL=dL12+dL3+dL4; */
            if (L != 0.0)
            {
                dL = (oldL - L) / L;
            }
        }
        if (it % 50 == 0)
        {
            printf("\n %i L12= %lf, L3= %lf, L4= %lf, L=%lf, dL= %lf",
                   it, 1.0e6 * L12, 1.0e6 * L3, 1.0e6 * L4, 1.0e6 * L, dL);
        }

        if (oldL < L && it > 0 && 1 == 1)
        {
            dt = dt / 2;
            printf("\n dt reduced: %i, dt=%lf, dL=%lf, oldL=%lf, L=%lf",
                   it, dt, dL, 1.0e6 * oldL, 1.0e6 * L);
            dL = 1.0;
            /*
#ifdef _OPENMP
#pragma omp parallel for private (i)
#endif
for(i=0;i<nxny;i++)
{
Bx[i]=Bx1[i]=Bxold[i];
By[i]=By1[i]=Byold[i];
Bz[i]=Bz1[i]=Bzold[i];
}
*/
            oldL = L;
        }
        else
        {
            if (it > 0)
            {
                dt = dt * 1.01;
            }
            oldL12 = L12;
            oldL3 = L3;
            oldL4 = L4;
            oldL5 = L5;
            oldL = L;
        }
/********** Iterate for new B **********/
#ifdef _OPENMP
#pragma omp parallel for private(i, ix, iy)
#endif
        for (ix = 0; ix < nx; ix++)
            for (iy = 0; iy < ny; iy++)
            {
                i = ny * ix + iy;
                Bx1[i] = Bx[i] + dt * (mu1 * (-2 * term1a * Bz[i] + 4 * term1c * Bx[i]) - mu3 * 2 * (Bx[i] - Bxo[i]) - mu4 * term4a[i] + mu2 * (4 * term2a * x[ix] * Bx[i] + 4 * term2b * y[iy] * Bx[i] - 2 * term2c * y[iy] * Bz[i]));
                By1[i] = By[i] + dt * (mu1 * (-2 * term1b * Bz[i] + 4 * term1c * By[i]) - mu3 * 2 * (By[i] - Byo[i]) - mu4 * term4b[i] + mu2 * (4 * term2a * x[ix] * By[i] + 4 * term2b * y[iy] * By[i] + 2 * term2c * x[ix] * Bz[i]));
                Bz1[i] = Bz[i] + dt * (-mu3 * 2 * (Bz[i] - Bzo[i]) - mu4 * term4c[i]);
            }
        /********** Halpha terms ******/
        if (mu5 != 0.0)
        {
            term5 = L5 = 0.0;
#ifdef _OPENMP
#pragma omp parallel for private(i, ix, iy) reduction(+ \
                                                      : L5)
#endif
            for (ix = 0; ix < nx; ix++)
                for (iy = 0; iy < ny; iy++)
                {
                    i = ny * ix + iy;
                    term5 = Bx[i] * Hy[i] - By[i] * Hx[i];
                    Bx1[i] = Bx1[i] - dt * w[i] * mu5 * term5 * Hy[i];
                    By1[i] = By1[i] + dt * w[i] * mu5 * term5 * Hx[i];
                    L5 = L5 + term5 * term5;
                }
            L5 = dxdy * L5 / Emag;
            if (it % 50 == 0)
            {
                printf(" L5= %lf", 1.0e6 * L5);
            }
        }
/********** Update B **********/
#ifdef _OPENMP
#pragma omp parallel for private(i)
#endif
        for (i = 0; i < nxny; i++)
        {
            /*
Bxold[i]=Bx[i];
Byold[i]=By[i];
Bzold[i]=Bz[i];
*/
            Bx[i] = Bx1[i];
            By[i] = By1[i];
            Bz[i] = Bz1[i];
        }
    }
    /*End of Iteration*/
    printf("\n\n End of Iteration");
    printf("\n mu3= %lf \t mu4= %lf \t mu5= %lf", mu3, mu4, mu5);
    printf("\n %i L12= %lf, L3= %lf, L4= %lf, L=%lf, dL= %lf",
           it, 1.0e6 * L12, 1.0e6 * L3, 1.0e6 * L4, 1.0e6 * L, dL);
/* Output data */
#ifdef _OPENMP
#pragma omp parallel for private(i)
#endif
    for (i = 0; i < nxny; i++)
    {
        Bx[i] = Bx[i] * Bave;
        By[i] = By[i] * Bave;
        Bz[i] = Bz[i] * Bave;
    }

    if ((streamw = fopen("output.dat", "w")) == NULL)
    {
        printf("\n Error output.dat ");
        exit(1);
    }
    for (iy = 0; iy < ny; iy++)
        for (ix = 0; ix < nx; ix++)
        {
            i = ny * ix + iy;
            dummy1 = Bx[i];
            fprintf(streamw, "%lf\n", dummy1);
            dummy1 = By[i];
            fprintf(streamw, "%lf\n", dummy1);
            dummy1 = Bz[i];
            fprintf(streamw, "%lf\n", dummy1);
        }
    fclose(streamw);
    printf("\n Preprocessed Vectormagnetogram output.dat saved \n");

    /*
if((streamw = fopen("test.dat","w")) == NULL) { printf("\n Error test.dat "); exit(1);}
for(iy=0;iy<ny;iy++)
for(ix=0;ix<nx;ix++)
{
i=ny*ix+iy; 
dummy1=Hx[i];
fprintf(streamw,"%lf\n",dummy1);
dummy1=Hy[i];
fprintf(streamw,"%lf\n",dummy1);
dummy1=w[i];
fprintf(streamw,"%lf\n",dummy1);
}
fclose(streamw);
*/
    printf("\n\n");
}
