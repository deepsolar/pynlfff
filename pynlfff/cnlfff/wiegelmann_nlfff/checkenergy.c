/*
 * @Description: https://doi.org/10.1007/s11207-012-9966-z
 * @Author: Thomas Wiegelmann (wiegelmann@mps.mpg.de)
 * @Date: 
 * @LastEditors: Thomas Wiegelmann (wiegelmann@mps.mpg.de)
 * @LastEditTime: 
*/

/* checkenergy.c */
#include <stdio.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>

main(int argc, char *argv[1])
{
    FILE *streamw, *streamw2, *streamw3, *initfile;
    double *x, *y, *z;
    double *Bx, *By, *Bz, *Bx0, *By0, *Bz0, *B, *B0;
    double totB0, totB, vc, vc1, vc2, vc3, cs, nve, nve1, nve2, mve;
    char leer[5];
    double dummy;
    int nx, ny, nz, nynz, nxnynz, nxny, nave, nd;
    int i, ix, iy, iz, i2, k;
    int nxnynzall, nynzall, orignd;
    if (argc < 3)
    {
        printf("\n\n Provide 2 INPUT FILES \n\n");
        exit(1);
    }

    if ((initfile = fopen("grid.ini", "r")) == NULL)
    {
        printf("\n Error");
        exit(1);
    }
    fscanf(initfile, "%s %i", &leer, &nx);
    fscanf(initfile, "%s %i", &leer, &ny);
    fscanf(initfile, "%s %i", &leer, &nz);
    fscanf(initfile, "%s %lf", &leer, &dummy);
    fscanf(initfile, "%s %i", &leer, &nd);
    fclose(initfile);
    printf("\n nx= %i, ny=%i , nz= %i, nd=%i \n", nx, ny, nz, nd);

    orignd = nd;
    nxnynzall = nx * ny * nz;
    nynzall = ny * nz;
    B0 = (double *)calloc(3 * nxnynzall, sizeof(double));
    B = (double *)calloc(3 * nxnynzall, sizeof(double));

    /* Read B from file */
    if ((streamw = fopen(argv[1], "rb")) == NULL)
    {
        printf("\n Read Error **.bin");
        exit(1);
    }
    fread(B0, sizeof(double) * 3 * nxnynzall, 1, streamw);
    fclose(streamw);
    printf("\n B0-field loaded \n ");
    if ((streamw = fopen(argv[2], "rb")) == NULL)
    {
        printf("\n Read Error **.bin");
        exit(1);
    }
    fread(B, sizeof(double) * 3 * nxnynzall, 1, streamw);
    fclose(streamw);
    printf("\n B-field loaded \n ");
    /* First full box then inner region*/
    for (k = 0; k < 2; k++)
    {
        if (k == 0)
        {
            nd = 0;
        }
        else
        {
            nd = orignd;
        }
        nx = nx - 2 * nd;
        ny = ny - 2 * nd;
        nz = nz - nd;

        nynz = ny * nz;
        nxnynz = nx * ny * nz;
        nxny = nx * ny;
        if (nd != 0)
        {
            printf("\nInner Box nx= %i, ny=%i , nz= %i \n", nx, ny, nz);
        }

        Bx0 = (double *)calloc(nxnynz, sizeof(double));
        By0 = (double *)calloc(nxnynz, sizeof(double));
        Bz0 = (double *)calloc(nxnynz, sizeof(double));
        Bx = (double *)calloc(nxnynz, sizeof(double));
        By = (double *)calloc(nxnynz, sizeof(double));
        Bz = (double *)calloc(nxnynz, sizeof(double));
        totB0 = totB = 0.0;
        vc = vc1 = vc2 = vc3 = 0.0;
        cs = nve = mve = 0.0;
        for (ix = 0; ix < nx; ix++)
            for (iy = 0; iy < ny; iy++)
                for (iz = 0; iz < nz; iz++)
                {
                    i = ix * nynz + iy * nz + iz;
                    i2 = (ix + nd) * nynzall + (iy + nd) * (nz + nd) + iz;
                    Bx0[i] = B0[i2];
                    By0[i] = B0[i2 + nxnynzall];
                    Bz0[i] = B0[i2 + 2 * nxnynzall];
                    Bx[i] = B[i2];
                    By[i] = B[i2 + nxnynzall];
                    Bz[i] = B[i2 + 2 * nxnynzall];
                    vc1 = vc1 + Bx0[i] * Bx0[i] + By0[i] * By0[i] + Bz0[i] * Bz0[i];
                    vc2 = vc2 + Bx[i] * Bx[i] + By[i] * By[i] + Bz[i] * Bz[i];
                    vc3 = vc3 + Bx0[i] * Bx[i] + By0[i] * By[i] + Bz0[i] * Bz[i];
                    cs = cs + (Bx0[i] * Bx[i] + By0[i] * By[i] + Bz0[i] * Bz[i]) /
                                  sqrt(Bx0[i] * Bx0[i] + By0[i] * By0[i] + Bz0[i] * Bz0[i]) / sqrt(Bx[i] * Bx[i] + By[i] * By[i] + Bz[i] * Bz[i]);
                    nve1 = nve1 + sqrt((Bx0[i] - Bx[i]) * (Bx0[i] - Bx[i]) +
                                       (By0[i] - By[i]) * (By0[i] - By[i]) + (Bz0[i] - Bz[i]) * (Bz0[i] - Bz[i]));
                    nve2 = nve2 + sqrt(Bx0[i] * Bx0[i] + By0[i] * By0[i] + Bz0[i] * Bz0[i]);
                    mve = mve + sqrt((Bx0[i] - Bx[i]) * (Bx0[i] - Bx[i]) +
                                     (By0[i] - By[i]) * (By0[i] - By[i]) + (Bz0[i] - Bz[i]) * (Bz0[i] - Bz[i])) /
                                    sqrt(Bx0[i] * Bx0[i] + By0[i] * By0[i] + Bz0[i] * Bz0[i]);
                    totB0 = totB0 + Bx0[i] * Bx0[i] + By0[i] * By0[i] + Bz0[i] * Bz0[i];
                    totB = totB + Bx[i] * Bx[i] + By[i] * By[i] + Bz[i] * Bz[i];
                }
        /* correlations */
        vc = vc3 / sqrt(vc1 * vc2);
        cs = cs / nx / ny / nz;
        nve = nve1 / nve2;
        mve = mve / nx / ny / nz;
        printf("\n Vector Correlation   VC = %lf", vc);
        printf("\n Cauchy Schwarz       CS = %lf", cs);
        printf("\n Norm Vector Error    NVE= %lf", nve);
        printf("\n Mean Vector Error    MVE= %lf", mve);
        /* printf("\n\n Int B0^2= %lf, Int B^2= %lf",totB0,totB); */
        printf("\n Relative magnetic Energy= %lf \n\n", totB / totB0);
        if (k == 0)
        {
            if ((streamw = fopen("Energy.log", "w")) == NULL)
            {
                printf("\n Energy.log");
                exit(1);
            }
            fprintf(streamw, "\n Input Files: %s, %s  \n", argv[1], argv[2]);
            fprintf(streamw, "\n Full Box, nx=%i, ny=%i,nz=%i, nd=%i \n", nx, ny, nz, orignd);
        }
        else
        {
            fprintf(streamw, "\n\n Inner Region, nx=%i, ny=%i,nz=%i \n", nx, ny, nz);
        }
        fprintf(streamw, "\n Vector Correlation   VC = %lf", vc);
        fprintf(streamw, "\n Cauchy Schwarz       CS = %lf", cs);
        fprintf(streamw, "\n Norm Vector Error    NVE= %lf", nve);
        fprintf(streamw, "\n Mean Vector Error    MVE= %lf", mve);
        fprintf(streamw, "\n Relative magnetic Energy= %lf", totB / totB0);
        fprintf(streamw, "\n -------------------------------------------------------------------");
    }
    fclose(streamw);
    printf("\nEnergy.log written \n\n");
}
