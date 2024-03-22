/*
 * @Description: https://doi.org/10.1007/s11207-012-9966-z
 * @Author: Thomas Wiegelmann (wiegelmann@mps.mpg.de)
 * @Date: 
 * @LastEditors: Thomas Wiegelmann (wiegelmann@mps.mpg.de)
 * @LastEditTime: 
*/

/* checkquality.c */
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
/* Macros */

#define MCENTERGRAD(f, id) ((f[i + id] - f[i - id]) / (2 * h))
#define MLEFTGRAD(f, id) ((-3 * f[i] + 4 * f[i + id] - f[i + 2 * id]) / (2 * h))
#define MRIGHTGRAD(f, id) ((+3 * f[i] - 4 * f[i - id] + f[i - 2 * id]) / (2 * h))

/* GRAD for Boundaries , all 3 differences needed */
#define GRADX(f, i) ((ix > 0 && ix < nx - 1) ? (MCENTERGRAD(f, nynz)) : ((ix == 0) ? (MLEFTGRAD(f, nynz)) : ((ix == nx - 1) ? (MRIGHTGRAD(f, nynz)) : (0.0))))
#define GRADY(f, i) ((iy > 0 && iy < ny - 1) ? (MCENTERGRAD(f, nz)) : ((iy == 0) ? (MLEFTGRAD(f, nz)) : ((iy == ny - 1) ? (MRIGHTGRAD(f, nz)) : (0.0))))
#define GRADZ(f, i) ((iz > 0 && iz < nz - 1) ? (MCENTERGRAD(f, 1)) : ((iz == 0) ? (MLEFTGRAD(f, 1)) : ((iz == nz - 1) ? (MRIGHTGRAD(f, 1)) : (0.0))))

main(int argc, char *argv[1])
{
    FILE *streamw, *streamw2, *streamw3, *initfile;
    double *x, *y, *z;
    double *Bx, *By, *Bz, *B;
    float *oxa, *oya, *oza, *oxb, *oyb, *ozb, *DivB, *Jx, *Jy, *Jz;
    double bx, by, bz, cbx, cby, cbz, fx, fy, fz;
    double divB, b2, helpL, helpf, helpL1, helpL2, h;
    double o2a, o2b;
    double j3d, jb1, jxb, sigi, totj3d, totsig, sigj, angle;
    double dummy, Bave;
    char leer[5];

    int nx, ny, nz, nynz, nxnynz, nxny, nave, nd;
    int i, ix, iy, iz, i2, k;
    int nxnynzall, nynzall, orignd;
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
    fscanf(initfile, "%s %lf", &leer, &dummy);
    fscanf(initfile, "%s %i", &leer, &nd);
    fclose(initfile);
    printf("\n nx= %i, ny=%i , nz= %i, nd=%i \n", nx, ny, nz, nd);
    orignd = nd;
    nxnynzall = nx * ny * nz;
    nynzall = ny * nz;
    B = (double *)calloc(3 * nxnynzall, sizeof(double));

    /* Read B from file */
    if ((streamw = fopen(argv[1], "rb")) == NULL)
    {
        printf("\n Read Error **.bin");
        exit(1);
    }
    fread(B, sizeof(double) * 3 * nxnynzall, 1, streamw);
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

        Bx = (double *)calloc(nxnynz, sizeof(double));
        By = (double *)calloc(nxnynz, sizeof(double));
        Bz = (double *)calloc(nxnynz, sizeof(double));
        /*
for(i=0;i<nxnynz;i++)
{
Bx[i]=B[i];
By[i]=B[i+nxnynz];
Bz[i]=B[i+2*nxnynz];
}
*/
        for (ix = 0; ix < nx; ix++)
            for (iy = 0; iy < ny; iy++)
                for (iz = 0; iz < nz; iz++)
                {
                    i = ix * nynz + iy * nz + iz;
                    i2 = (ix + nd) * nynzall + (iy + nd) * (nz + nd) + iz;
                    Bx[i] = B[i2];
                    By[i] = B[i2 + nxnynzall];
                    Bz[i] = B[i2 + 2 * nxnynzall];
                }
        /* free(B); */
        /*******************************************************************************/
        /* Check quality of force.-free fields, added 09.08.2011  **********************/
        /*******************************************************************************/

        oxa = (float *)calloc(nxnynz, sizeof(float));
        oya = (float *)calloc(nxnynz, sizeof(float));
        oza = (float *)calloc(nxnynz, sizeof(float));
        oxb = (float *)calloc(nxnynz, sizeof(float));
        oyb = (float *)calloc(nxnynz, sizeof(float));
        ozb = (float *)calloc(nxnynz, sizeof(float));
        DivB = (float *)calloc(nxnynz, sizeof(float));
        /*Jx =(float *) calloc(nxnynz, sizeof(float));
Jy =(float *) calloc(nxnynz, sizeof(float));
Jz =(float *) calloc(nxnynz, sizeof(float));*/

        /* nave=sqrt(1.0*(nx-2*nd-1)*(ny-2*nd-1)); */
        nave = sqrt(1.0 * (nx - 1) * (ny - 1));
        h = 1.0 / nave;
        printf("\n h= %lf", h);

        /* norm B */
        iz = 0;
        Bave = 0.0;
        /* for(ix=nd;ix<nx-nd;ix++)
for(iy=nd;iy<ny-nd;iy++) */
        for (ix = 0; ix < nx; ix++)
            for (iy = 0; iy < ny; iy++)
            {
                i = nynz * ix + nz * iy + iz;
                Bave = Bave + sqrt(Bx[i] * Bx[i] + By[i] * By[i] + Bz[i] * Bz[i]);
            }
        /* Bave=Bave/(nx-2*nd)/(ny-2*nd); */
        Bave = Bave / nx / ny;
        printf("\n Bave= %lf", Bave);
        for (i = 0; i < nxnynz; i++)
        {
            Bx[i] = Bx[i] / Bave;
            By[i] = By[i] / Bave;
            Bz[i] = Bz[i] / Bave;
        }

        helpL = helpL1 = helpL2 = 0.0;
        helpf = 0.0;
        totj3d = totsig = sigj = 0.0;
        for (ix = 0; ix < nx; ix++)
            for (iy = 0; iy < ny; iy++)
                for (iz = 0; iz < nz; iz++)
                {
                    i = ix * nynz + iy * nz + iz;
                    bx = Bx[i];
                    by = By[i];
                    bz = Bz[i];

                    b2 = (bx * bx + by * by + bz * bz);
                    cbx = GRADY(Bz, i) - GRADZ(By, i);
                    cby = GRADZ(Bx, i) - GRADX(Bz, i);
                    cbz = GRADX(By, i) - GRADY(Bx, i);
                    /*
Jx[i]=cbx;
Jy[i]=cby;
Jz[i]=cbz;
*/
                    fx = cby * bz - cbz * by;
                    fy = cbz * bx - cbx * bz;
                    fz = cbx * by - cby * bx;
                    divB = GRADX(Bx, i) + GRADY(By, i) + GRADZ(Bz, i);
                    DivB[i] = divB;

                    if (b2 > 0.0)
                    {
                        oxa[i] = (1.0 / b2) * (fx);
                        oya[i] = (1.0 / b2) * (fy);
                        oza[i] = (1.0 / b2) * (fz);
                        oxb[i] = (1.0 / b2) * (divB * bx);
                        oyb[i] = (1.0 / b2) * (divB * by);
                        ozb[i] = (1.0 / b2) * (divB * bz);
                        o2a = oxa[i] * oxa[i] + oya[i] * oya[i] + oza[i] * oza[i];
                        o2b = oxb[i] * oxb[i] + oyb[i] * oyb[i] + ozb[i] * ozb[i];
                        helpL = helpL + b2 * o2a + b2 * o2b;
                        helpL1 = helpL1 + b2 * o2a;
                        helpL2 = helpL2 + b2 * o2b;
                    }
                    /* Calculate Angle between field and Current */

                    j3d = sqrt(cbx * cbx + cby * cby + cbz * cbz);
                    jb1 = j3d * sqrt(b2);
                    jxb = sqrt(fx * fx + fy * fy + fz * fz);
                    sigi = 0.0;
                    if (jb1 > 0.0)
                    {
                        sigi = jxb / jb1;
                        // printf("sigi=%.4lf",sigi);
                    }
                    // else{
                    //     // printf("=0=");
                    // }
                    totj3d = totj3d + j3d; //这个值较小，但是比下面大
                    /* totsig=totsig+sigi; */
                    // totsig=totsig+sigi;
                    totsig = totsig + j3d * sigi; //这个值过大
                }
        helpL = helpL * h * h * h;
        helpL1 = helpL1 * h * h * h;
        helpL2 = helpL2 * h * h * h;
        sigj = totsig / totj3d;                  // totj3d较小导致0.9
        angle = asin(sigj) * 180.0 / 3.14159265; // sigj接近0.9甚至是1导致 angle在60附近    sigj越接近0越好
        if (k == 0)
        {
            printf("\n Full computational Box");
        }
        else
        {
            printf("\n Inner physical Region");
        }
        printf("\n L=%.4lf, L1=%.4lf,  L2= %.4lf", helpL, helpL1, helpL2);
        printf("\n Sigma_J %.4lf , Angle = %.4lf Degree", sigj, angle);

        if (k == 0)
        {
            if ((streamw = fopen("NLFFFquality.log", "w")) == NULL)
            {
                printf("\n Error NLFFFquality.log");
                exit(1);
            }
            fprintf(streamw, "\n Quality Check of NLFFF field");
            fprintf(streamw, "\n Input File: %s  \n", argv[1]);
            fprintf(streamw, "\n Full Box, nx=%i, ny=%i,nz=%i, nd=%i \n", nx, ny, nz, orignd);
        }
        else
        {
            fprintf(streamw, "\n\n Inner Region, nx=%i, ny=%i,nz=%i \n", nx, ny, nz);
        }
        fprintf(streamw, "\n Average B on lower Boundary: %.2lf", Bave);
        fprintf(streamw, "\n L=%.4lf, L1=%.4lf,  L2= %.4lf", helpL, helpL1, helpL2);
        fprintf(streamw, "\n Sigma_J %.4lf , Angle(B,J) = %.4lf Degree", sigj, angle);
        fprintf(streamw, "\n -------------------------------------------------------------------");
        free(Bx);
        free(By);
        free(Bz);
        free(oxa);
        free(oya);
        free(oza);
        free(oxb);
        free(oyb);
        free(ozb);
        free(DivB);
    }
    fclose(streamw);
    printf("\n\n Results written to: NLFFFquality.log \n\n");
}
