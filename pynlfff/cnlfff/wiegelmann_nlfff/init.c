/*
 * @Description: https://doi.org/10.1007/s11207-012-9966-z
 * @Author: Thomas Wiegelmann (wiegelmann@mps.mpg.de)
 * @Date: 
 * @LastEditors: Thomas Wiegelmann (wiegelmann@mps.mpg.de)
 * @LastEditTime: 
*/

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include "globals.h"
#ifdef _OPENMP
#include <omp.h>
#endif
double bx(double x0, double y0, double z0);
double by(double x0, double y0, double z0);
double bz(double x0, double y0, double z0);
double babs(double x0, double y0, double z0);
void init(double alpha_dummy)
{
    char leer;
    double dummy1, dummy4; /* dummy5; */
    double x0, y0, z0;     /* bx0, by0, bz0; */
    double Lnorm;
    int m, n; /* dummy2, dummy3; */
    int i, ix, iy, iz;
    pi = 3.14159;
    /* Read Input-Parameter */
    if ((initfile = fopen("param1.ini", "r")) == NULL)
    {
        printf("\n Error");
        exit(1);
    }
    fscanf(initfile, "%s %i", &leer, &maxm);
    fscanf(initfile, "%s %i", &leer, &maxn);
    fscanf(initfile, "%s %lf", &leer, &Lx);
    fscanf(initfile, "%s %lf", &leer, &Ly);
    fscanf(initfile, "%s %lf", &leer, &Lz);
    fclose(initfile);
    Lz = Lx * (nz - 1) / (nx - 1);

    Lx = Lx * Ls;
    Ly = Ly * Ls;
    Lz = Lz * Ls;
    printf("\n\n Input Parameter ");
    printf("\n maxm= %i \t maxn= %i", maxm, maxn);
    printf("\n Lx= %lf \t Ly= %lf \t Lz= %lf", Lx, Ly, Lz);
    Lnorm = sqrt(2.0 / (1.0 / (Lx * Lx) + 1.0 / (Ly * Ly)));
    alpha = alpha / Lnorm;
    /* printf("\n alpha =%lf", (1.0e6)*alpha); */
    printf("\n norm alpha =%lf", Lnorm * alpha);
    printf("\n Limit alpha < %lf \t alpha*Lx< %lf", (1.0e6) * pi * sqrt(1. / (Lx * Lx) + 1. / (Ly * Ly)), pi * sqrt(2.0));
    if (fabs(Lnorm * alpha) > pi * sqrt(2.0))
    {
        printf("\n\n alpha out of range \n");
        exit(0);
    }

    /* Read Data */
    for (m = 0; m < 102; m++)
        for (n = 0; n < 102; n++)
        {
            Cmn[m][n] = lmn[m][n] = rmn[m][n] = 0.0;
        }
    if ((initfile = fopen("Cmn1.ini", "r")) == NULL)
    {
        printf("\n Error Cmn");
        exit(1);
    }
    for (n = 0; n < maxn + 1; n++)
        for (m = 0; m < maxm + 1; m++)
        {
            fscanf(initfile, "%lf", &dummy1);
            Cmn[m][n] = dummy1;
        }
    fclose(initfile);

    /* Calculate lmn and rmn */
    for (m = 1; m < maxm + 1; m++)
        for (n = 1; n < maxn + 1; n++)
        {
            lmn[m][n] = pi * pi * (m * m / (Lx * Lx) + n * n / (Ly * Ly));
            rmn[m][n] = sqrt(lmn[m][n] - alpha * alpha);
        }
    dx = Lx / (nxmax - 1);
    printf("\n dx= %lf", dx / (1.0e6));
    i = (nxmax - nx) / 2;
    for (ix = 0; ix < nx; ix++)
    {
        x[ix] = (i + ix) * dx;
    }
    for (iy = 0; iy < ny; iy++)
    {
        y[iy] = (i + iy) * dx;
    }
    for (iz = 0; iz < nz; iz++)
    {
        z[iz] = iz * dx;
    }

    /* Rand weg, wo B null wird */

    for (ix = 0; ix < nx; ix++)
    {
        x[ix] = Lx * 0.005 + ix * 0.99 * Lx / (nx - 1);
    }
    for (iy = 0; iy < ny; iy++)
    {
        y[iy] = Ly * 0.005 + iy * 0.99 * Ly / (ny - 1);
    }
    for (iz = 0; iz < nz; iz++)
    {
        z[iz] = iz * 0.99 * Lz / (nz - 1);
    }

    for (i = 0; i < nxnynz; i++)
    {
        Bx[i] = By[i] = Bz[i] = 0.0;
    }

    if (calcb == 1)
    {
        printf("\n Initialize B");
#ifdef _OPENMP
#pragma omp parallel for private(i, ix, iy, iz, x0, y0, z0)
#endif
        for (ix = 0; ix < nx; ix++)
        {
            printf("\n . %i", ix);
            for (iy = 0; iy < ny; iy++)
                for (iz = 0; iz < nz; iz++)
                {
                    i = nynz * ix + nz * iy + iz;
                    x0 = x[ix];
                    y0 = y[iy];
                    z0 = z[iz];
                    Bx[i] = bx(x0, y0, z0);
                    By[i] = by(x0, y0, z0);
                    Bz[i] = bz(x0, y0, z0);
                }
        }
        /******* Binary Output *******************/
        /*
#ifdef _OPENMP
#pragma omp parallel for private (i) 
#endif
for(i=0;i<nxnynz;i++)
{
B[i]=Bx[i];
B[i+nxnynz]=By[i];
B[i+2*nxnynz]=Bz[i];
}
*/
        if ((streamw = fopen("B0.bin", "wb")) == NULL)
        {
            printf("\n Error B0.bin");
            exit(1);
        }
        /* fwrite(B,sizeof(double)*3*nxnynz,1,streamw); */
        fwrite(Bx, sizeof(double) * nxnynz, 1, streamw);
        fwrite(By, sizeof(double) * nxnynz, 1, streamw);
        fwrite(Bz, sizeof(double) * nxnynz, 1, streamw);
        fclose(streamw);
        printf("\t done ");
        printf("\n Potential field saved in B0.bin \n\n");
        exit(0);
    }
    /***************************************************************************/
    else if (calcb == 2) /******* Read from asci *********************************/
    {
        dummy4 = 0.0;
        if ((streamw = fopen("B.dat", "r")) == NULL)
        {
            printf("\n Error B.dat");
            exit(1);
        }
        for (ix = 0; ix < nx; ix++)
            for (iy = 0; iy < ny; iy++)
                for (iz = 0; iz < nz; iz++)
                {
                    i = nynz * ix + nz * iy + iz;
                    fscanf(streamw, "%lf", &dummy1);
                    Bx[i] = dummy1;
                    fscanf(streamw, "%lf", &dummy1);
                    By[i] = dummy1;
                    fscanf(streamw, "%lf", &dummy1);
                    Bz[i] = dummy1;
                    dummy4 = dummy4 + sqrt(Bx[i] * Bx[i] + By[i] * By[i] + Bz[i] * Bz[i]);
                }
        fclose(streamw);
        printf("\n Low + Lou read finished \n");
    }
    /*************************************************************/
    else /******* Read from bin *********************************/
    {
        if ((streamw = fopen("B0.bin", "rb")) == NULL)
        {
            printf("\n Error B.bin");
            exit(1);
        }
        /* fread(B,sizeof(double)*3*nxnynz,1,streamw); */
        fread(Bx, sizeof(double) * nxnynz, 1, streamw);
        fread(By, sizeof(double) * nxnynz, 1, streamw);
        fread(Bz, sizeof(double) * nxnynz, 1, streamw);
        printf("\t Read finished ");
        /*
for(i=0;i<nxnynz;i++)
{
Bx[i]=B[i];
By[i]=B[i+nxnynz];
Bz[i]=B[i+2*nxnynz];
}
*/
        printf("\t Binary read finished ");
    }
}
