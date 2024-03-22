/*
 * @Description: https://doi.org/10.1007/s11207-012-9966-z
 * @Author: Thomas Wiegelmann (wiegelmann@mps.mpg.de)
 * @Date: 
 * @LastEditors: Thomas Wiegelmann (wiegelmann@mps.mpg.de)
 * @LastEditTime: 
*/

/* rebin2d.c */
/* Contact Arrays for multigrid NLFFF-code */
#include <stdio.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>

main(int argc, char *argv[])
{
    FILE *streamw, *streamw2, *streamw3, *initfile;
    double *x, *y, *z;
    double *Bx, *By, *Bz, *B;
    double *Bx2, *By2, *Bz2, *B2;
    char leer[5];
    double dummy, dummy1, mue;
    int nx, ny, nz, nynz, nxnynz, nxny, nd;
    int nx2, ny2, nz2, nxny2, nd2;
    int i, ix, iy, iz;
    int i2, ix2, iy2, iz2;
    int i3, ix3, iy3, iz3;
    nd = 0;
    if (argc < 2)
    {
        printf("\n\n NO INPUT FILE GIVEN \n\n");
        exit(1);
    }
    if (argc < 3)
    {
        printf("\n\n NO OUTPUT FILE GIVEN \n\n");
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
    fscanf(initfile, "%s %lf", &leer, &mue);
    fscanf(initfile, "%s %i", &leer, &nd);
    fclose(initfile);

    printf("\n nx= %i, ny=%i , nz= %i, nd= %i \n", nx, ny, nz, nd);

    nxny = nx * ny;

    Bx = (double *)calloc(nxny, sizeof(double));
    By = (double *)calloc(nxny, sizeof(double));
    Bz = (double *)calloc(nxny, sizeof(double));

    if ((streamw = fopen(argv[1], "r")) == NULL)
    {
        printf("\n Error reading");
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
    printf("\n Vectormagnetogram %s reading done ", argv[1]);

    /* Still to write rebin procedure */
    nx2 = nx / 2;
    ny2 = ny / 2;
    nz2 = nz / 2;
    nd2 = nd / 2;
    printf("\n Writing minigrid.ini ");
    if ((streamw = fopen("minigrid.ini", "w")) == NULL)
    {
        printf("\n Error writing");
        exit(1);
    }
    fprintf(streamw, "nx \n");
    fprintf(streamw, "\t %i \n", nx2);
    fprintf(streamw, "ny \n");
    fprintf(streamw, "\t %i \n", ny2);
    fprintf(streamw, "nz \n");
    fprintf(streamw, "\t %i \n", nz2);
    fprintf(streamw, "mu \n");
    fprintf(streamw, "\t %lf \n", mue);
    fprintf(streamw, "nd \n");
    fprintf(streamw, "\t %i", nd2);
    fclose(streamw);

    nxny2 = nx2 * ny2;
    Bx2 = (double *)calloc(nxny2, sizeof(double));
    By2 = (double *)calloc(nxny2, sizeof(double));
    Bz2 = (double *)calloc(nxny2, sizeof(double));
    // nx=8 ny=6 nz=4
    // nx2=4 ny2=3 nz2=2
    for (iy2 = 0; iy2 < ny2; iy2++)     //iy = 0 1 2
        for (ix2 = 0; ix2 < nx2; ix2++) // ix = 0 1 2 3
        {
            i2 = ny2 * ix2 + iy2; // i2 = 3*0+0=0
            ix = ix2 * 2;         //ix = 0*2=0
            iy = iy2 * 2;         //iy = 0*2=0
            i = ny * ix + iy;     // i= 6*0+0=0
            Bx2[i2] = (Bx[i] + Bx[i + 1] + Bx[i + ny] + Bx[i + ny + 1]) / 4;
            // Bx2[0]=(bx0+bx1+bx(0+6)+bz(0+6+1))/4  取周围四个平均变成新值，这样就压缩一半了
            By2[i2] = (By[i] + By[i + 1] + By[i + ny] + By[i + ny + 1]) / 4;
            Bz2[i2] = (Bz[i] + Bz[i + 1] + Bz[i + ny] + Bz[i + ny + 1]) / 4;
        }

    /***********************************************************************************/
    if ((streamw = fopen(argv[2], "w")) == NULL)
    {
        printf("\n Error writing");
        exit(1);
    }
    for (iy2 = 0; iy2 < ny2; iy2++)
        for (ix2 = 0; ix2 < nx2; ix2++)
        {
            i2 = ny2 * ix2 + iy2;
            dummy1 = Bx2[i2];
            fprintf(streamw, "%lf\n", dummy1);
            dummy1 = By2[i2];
            fprintf(streamw, "%lf\n", dummy1);
            dummy1 = Bz2[i2];
            fprintf(streamw, "%lf\n", dummy1);
        }
    fclose(streamw);
    printf("\n\n Rebinned B written to %s done ", argv[2]);

    printf("\n\n");
}
