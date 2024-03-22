/*
 * @Description: https://doi.org/10.1007/s11207-012-9966-z
 * @Author: Thomas Wiegelmann (wiegelmann@mps.mpg.de)
 * @Date: 
 * @LastEditors: Thomas Wiegelmann (wiegelmann@mps.mpg.de)
 * @LastEditTime: 
*/

/* saveboundary.c */
#include <stdio.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>

#define DUMP                          \
    i = nynz * ix + nz * iy + iz;     \
    fprintf(streamw, "%lf\n", Bx[i]); \
    fprintf(streamw, "%lf\n", By[i]); \
    fprintf(streamw, "%lf\n", Bz[i]);

main(int argc, char *argv[1])
{
    FILE *streamw, *streamw2, *streamw3, *initfile;
    double *x, *y, *z;
    double *Bx, *By, *Bz, *B;
    char leer[5];
    double dummy;
    int nx, ny, nz, nynz, nxnynz, nxny;
    int i, ix, iy, iz;

    if (argc < 2)
    {
        printf("\n\n NO INPUT FILE GIVEN \n\n");
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
    fclose(initfile);
    printf("\n nx= %i, ny=%i , nz= %i \n", nx, ny, nz);
    nynz = ny * nz;
    nxnynz = nx * ny * nz;
    nxny = nx * ny;

    Bx = (double *)calloc(nxnynz, sizeof(double));
    By = (double *)calloc(nxnynz, sizeof(double));
    Bz = (double *)calloc(nxnynz, sizeof(double));
    B = (double *)calloc(3 * nxnynz, sizeof(double));

    /* Read B from file */
    if ((streamw = fopen(argv[1], "rb")) == NULL)
    {
        printf("\n Read Error **.bin");
        exit(1);
    }
    fread(B, sizeof(double) * 3 * nxnynz, 1, streamw);
    printf("\n B-field loaded \n ");
    for (i = 0; i < nxnynz; i++)
    {
        Bx[i] = B[i];
        By[i] = B[i + nxnynz];
        Bz[i] = B[i + 2 * nxnynz];
    }
    free(B);
    /* Output all components on all 6 boundaries */

    if ((streamw = fopen("allboundaries.dat", "w")) == NULL)
    {
        printf("\n Error ");
        exit(1);
    }
    iz = 0;
    for (iy = 0; iy < ny; iy++)
        for (ix = 0; ix < nx; ix++)
        {
            DUMP
        }
    iz = nz - 1;
    for (iy = 0; iy < ny; iy++)
        for (ix = 0; ix < nx; ix++)
        {
            DUMP
        }
    iy = 0;
    for (iz = 0; iz < nz; iz++)
        for (ix = 0; ix < nx; ix++)
        {
            DUMP
        }
    iy = ny - 1;
    for (iz = 0; iz < nz; iz++)
        for (ix = 0; ix < nx; ix++)
        {
            DUMP
        }
    ix = 0;
    for (iz = 0; iz < nz; iz++)
        for (iy = 0; iy < ny; iy++)
        {
            DUMP
        }
    ix = nx - 1;
    for (iz = 0; iz < nz; iz++)
        for (iy = 0; iy < ny; iy++)
        {
            DUMP
        }
    fclose(streamw);

    printf("\n\n");
}