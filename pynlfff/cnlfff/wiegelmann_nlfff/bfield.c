/*
 * @Description: https://doi.org/10.1007/s11207-012-9966-z
 * @Author: Thomas Wiegelmann (wiegelmann@mps.mpg.de)
 * @Date: 
 * @LastEditors: Thomas Wiegelmann (wiegelmann@mps.mpg.de)
 * @LastEditTime: 
*/

/**************************************************/
/********* B-Field solver   ***********************/
/**************************************************/
#include <stdio.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include "globals.h"
double bx(double x0, double y0, double z0)
{
    int m, n;
    double bx0;
    bx0 = 0.0;
    for (m = 1; m < maxm + 1; m++)
        for (n = 1; n < maxn + 1; n++)
        {
            bx0 = bx0 + q1 * ((Cmn[m][n] / lmn[m][n]) * exp(-rmn[m][n] * z0) *
                              (alpha * (pi * n / Ly) * sin(pi * m * x0 / Lx) * cos(pi * n * y0 / Ly) - rmn[m][n] * (pi * m / Lx) * cos(pi * m * x0 / Lx) * sin(pi * n * y0 / Ly)));
        }
    return bx0;
}

double by(double x0, double y0, double z0)
{
    int m, n;
    double by0;
    by0 = 0.0;
    for (m = 1; m < maxm + 1; m++)
        for (n = 1; n < maxn + 1; n++)
        {
            by0 = by0 - q1 * ((Cmn[m][n] / lmn[m][n]) * exp(-rmn[m][n] * z0) *
                              (alpha * (pi * m / Lx) * cos(pi * m * x0 / Lx) * sin(pi * n * y0 / Ly) + rmn[m][n] * (pi * n / Ly) * sin(pi * m * x0 / Lx) * cos(pi * n * y0 / Ly)));
        }
    return by0;
}

double bz(double x0, double y0, double z0)
{
    int m, n;
    double bz0;
    bz0 = 0.0;
    for (m = 1; m < maxm + 1; m++)
        for (n = 1; n < maxn + 1; n++)
        {
            bz0 = bz0 + q1 * (Cmn[m][n] * exp(-rmn[m][n] * z0) * sin(pi * m * x0 / Lx) * sin(pi * n * y0 / Ly));
        }
    return bz0;
}

double babs(double x0, double y0, double z0)
{
    double bx0, by0, bz0, btot;
    bx0 = bx(x0, y0, z0);
    by0 = by(x0, y0, z0);
    bz0 = bz(x0, y0, z0);
    btot = sqrt(bx0 * bx0 + by0 * by0 + bz0 * bz0);
    return btot;
}
/*********** Green function Solver ******************/

void green()
{
    FILE *streamw, *initfile;
    char leer[25];
    double *x, *y, *z, /* *Bx, *By, *Bz,*/ *Pot0, *bz0;
    double zoff, dummy1, h, r, rx, ry, rz;
    int nx, ny, nz, nynz, nxnynz;
    int i, i2, /*i3,*/ ix, iy, iz, ix1, iy1;
    h = 1.0;
    if ((initfile = fopen("grid.ini", "r")) == NULL)
    {
        printf("\n Error grid.ini");
        exit(1);
    }
    fscanf(initfile, "%s %i", &leer, &nx);
    fscanf(initfile, "%s %i", &leer, &ny);
    fscanf(initfile, "%s %i", &leer, &nz);
    fscanf(initfile, "%s %lf", &leer, &zoff);
    fclose(initfile);
    printf("\n nx= %i, ny=%i , nz= %i \n", nx, ny, nz);
    nynz = ny * nz;
    nxnynz = nx * ny * nz;
    zoff = 0.5;
    x = (double *)calloc(nx, sizeof(double));
    y = (double *)calloc(ny, sizeof(double));
    z = (double *)calloc(nz, sizeof(double));
    Pot0 = (double *)calloc(nxnynz, sizeof(double));
    /*
Bx =(double *) calloc(nxnynz, sizeof(double));
By =(double *) calloc(nxnynz, sizeof(double));
Bz =(double *) calloc(nxnynz, sizeof(double));
*/
    bz0 = (double *)calloc(nx * ny, sizeof(double));
    /*
if((streamw = fopen("bz.dat","r")) == NULL) { printf("\n Error bz.dat "); exit(1);}
for(iy=0;iy<ny;iy++)
for(ix=0;ix<nx;ix++)
{
i2=ny*ix+iy;
fscanf(streamw,"%lf", &dummy1);
bz0[i2]=dummy1;
}
fclose(streamw);
printf("\n Loading from bz.dat \n");
 */

    if ((streamw = fopen("allboundaries.dat", "r")) == NULL)
    {
        printf("\n Error ");
        exit(1);
    }
    for (iy = 0; iy < ny; iy++)
        for (ix = 0; ix < nx; ix++)
        {
            i2 = ny * ix + iy;
            fscanf(streamw, "%lf", &dummy1);
            fscanf(streamw, "%lf", &dummy1);
            fscanf(streamw, "%lf", &dummy1);
            bz0[i2] = dummy1;
        }
    fclose(streamw);
    printf("\n Vectormagnetogram loaded");
    printf("\n Only Bz is used for potential field \n");

    /***********************************************************/
    for (ix = 0; ix < nx; ix++)
    {
        x[ix] = ix * 1.0;
    }
    for (iy = 0; iy < ny; iy++)
    {
        y[iy] = iy * 1.0;
    }
    for (iz = 0; iz < nz; iz++)
    {
        z[iz] = zoff + iz * 1.0;
    }

/* Calculate Potential */
#ifdef _OPENMP
#pragma omp parallel for private(i, ix, iy, iz, dummy1, ix1, iy1, rx, ry, rz, r, i2)
#endif
    for (ix = 0; ix < nx; ix++)
    {
        printf("\n percent finished = %lf", 100.0 * ix / nx);
        for (iy = 0; iy < ny; iy++)
            for (iz = 0; iz < nz; iz++)
            {
                i = ix * nynz + iy * nz + iz;
                dummy1 = 0.0;
                for (ix1 = 0; ix1 < nx; ix1++)
                    for (iy1 = 0; iy1 < ny; iy1++)
                    {
                        i2 = ny * ix1 + iy1;
                        rx = x[ix] - x[ix1];
                        ry = y[iy] - y[iy1];
                        rz = z[iz];
                        r = sqrt(rx * rx + ry * ry + rz * rz);
                        dummy1 = dummy1 - bz0[i2] / r;
                    }
                Pot0[i] = dummy1 / 2.0 / 3.14159;
            }
    }
/* Write to Binary */
#ifdef _OPENMP
#pragma omp parallel for private(i, ix, iy, iz)
#endif
    for (ix = 0; ix < nx; ix++)
        for (iy = 0; iy < ny; iy++)
            for (iz = 0; iz < nz; iz++)
            {
                i = ix * nynz + iy * nz + iz;
                Bx[i] = GRADX(Pot0, i);
                By[i] = GRADY(Pot0, i);
                Bz[i] = GRADZ(Pot0, i);
            }

    if ((streamw = fopen("B0.bin", "wb")) == NULL)
    {
        printf("\n Error B0.bin");
        exit(1);
    }
    fwrite(Bx, sizeof(double) * nxnynz, 1, streamw);
    fwrite(By, sizeof(double) * nxnynz, 1, streamw);
    fwrite(Bz, sizeof(double) * nxnynz, 1, streamw);
    fclose(streamw);
    printf("\n\n B written to B0.bin \n");
}
