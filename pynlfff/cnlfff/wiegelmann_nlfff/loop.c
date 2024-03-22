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

#define DUMP                         \
    i = nynz * ix + nz * iy + iz;    \
    fscanf(streamw, "%lf", &dummy1); \
    Bx[i] = dummy1;                  \
    fscanf(streamw, "%lf", &dummy1); \
    By[i] = dummy1;                  \
    fscanf(streamw, "%lf", &dummy1); \
    Bz[i] = dummy1;
/*
double gradx(double *f, int i);
double grady(double *f, int i);
double gradz(double *f, int i);
*/
double bx(double x0, double y0, double z0);
double by(double x0, double y0, double z0);
double bz(double x0, double y0, double z0);
double babs(double x0, double y0, double z0);
/************************************************************************************/
void calculateJxB()
{
    double b2;
    int ix, iy, iz, i;

#ifdef _OPENMP
#pragma omp parallel for private(i, ix, iy, iz, b2)
#endif
    for (ix = 0; ix < nx - 0; ix++)
        for (iy = 0; iy < ny - 0; iy++)
            for (iz = 0; iz < nz - 0; iz++)
            {
                i = ix * nynz + iy * nz + iz;
                /***** J = curl B ***********/
                /*
Jx[i]=rmu0gausT*(GRADY(Bz,i)-GRADZ(By,i));
Jy[i]=rmu0gausT*(GRADZ(Bx,i)-GRADX(Bz,i));
Jz[i]=rmu0gausT*(GRADX(By,i)-GRADY(Bx,i));
*/
                /***** V = J x B  *********/
                /*
Vx[i]=gausT*(Jy[i]*Bz[i]-Jz[i]*By[i]);
Vy[i]=gausT*(Jz[i]*Bx[i]-Jx[i]*Bz[i]);
Vz[i]=gausT*(Jx[i]*By[i]-Jy[i]*Bx[i]);
*/

                Jx[i] = GRADY(Bz, i) - GRADZ(By, i);
                Jy[i] = GRADZ(Bx, i) - GRADX(Bz, i);
                Jz[i] = GRADX(By, i) - GRADY(Bx, i);

                Vx[i] = Jy[i] * Bz[i] - Jz[i] * By[i];
                Vy[i] = Jz[i] * Bx[i] - Jx[i] * Bz[i];
                Vz[i] = Jx[i] * By[i] - Jy[i] * Bx[i];

                /***** VxB = (V x B) / B^2 ****new *****/
                b2 = Bx[i] * Bx[i] + By[i] * By[i] + Bz[i] * Bz[i];
                if (b2 > 0.0)
                {
                    VxBx[i] = (Vy[i] * Bz[i] - Vz[i] * By[i]) / b2;
                    VxBy[i] = (Vz[i] * Bx[i] - Vx[i] * Bz[i]) / b2;
                    VxBz[i] = (Vx[i] * By[i] - Vy[i] * Bx[i]) / b2;
                }
                else
                {
                    VxBx[i] = 0.0;
                    VxBy[i] = 0.0;
                    VxBz[i] = 0.0;
                }
            }
}
void classicrelax()
{
    int ix, iy, iz, i;
    /* double nue0, nue, eta, dummy; */

#ifdef _OPENMP
#pragma omp parallel for private(i, ix, iy, iz)
#endif
    for (ix = 0; ix < nx - 0; ix++)
        for (iy = 0; iy < ny - 0; iy++)
            for (iz = 0; iz < nz - 0; iz++)
            {
                i = ix * nynz + iy * nz + iz;
                /***** rotV = curl(V x B)  *********/
                Rotvx[i] = GRADY(VxBz, i) - GRADZ(VxBy, i);
                Rotvy[i] = GRADZ(VxBx, i) - GRADX(VxBz, i);
                Rotvz[i] = GRADX(VxBy, i) - GRADY(VxBx, i);
            }
/****** add constant Resistivity eta J ***************/
/*
#ifdef _OPENMP
#pragma omp parallel for private (i,ix,iy,iz)
#endif
for(ix=0;ix<nx-0;ix++)
for(iy=0;iy<ny-0;iy++)
for(iz=0;iz<nz-0;iz++)
{
i=ix*nynz+iy*nz+iz;
Rotvx[i]=1.0*Rotvx[i]  -0.00002*(GRADY(Jz,i)-GRADZ(Jy,i));
Rotvy[i]=1.0*Rotvy[i]  -0.00002*(GRADZ(Jx,i)-GRADX(Jz,i));
Rotvz[i]=1.0*Rotvz[i]  -0.00002*(GRADX(Jy,i)-GRADY(Jx,i));
}
*/

/***** B(t+dt) = B(t)+ curl(V x B)  *********/
/*
nue0=nue=10.0*2.0e8;
nue=0.1e14;
nue=0.1e12;
*/
#ifdef _OPENMP
#pragma omp parallel for private(i, ix, iy, iz)
#endif
    for (ix = 1; ix < nx - 1; ix++)
        for (iy = 1; iy < ny - 1; iy++)
            for (iz = 1; iz < nz - 1; iz++)
            {
                i = ix * nynz + iy * nz + iz;
                Bx1[i] = Bx[i] + mue * Rotvx[i];
                By1[i] = By[i] + mue * Rotvy[i];
                Bz1[i] = Bz[i] + mue * Rotvz[i];
            }
}
/************************************************************************************/
void split()
{
    /* int i; */
    printf("\n\n Load Loop fields, Loop 1");
    if ((streamw = fopen("B1.bin", "rb")) == NULL)
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
Bx[i]=Bx[i]+B[i];
By[i]=By[i]+B[i+nxnynz];
Bz[i]=Bz[i]+B[i+2*nxnynz];
}
*/
    printf("\t Load Loop finished ");
}
/************************************************************************************/
void loadboundary()
{
    int ix, iy, iz, i;
    double dummy1;
    if ((streamw = fopen("allboundaries.dat", "r")) == NULL)
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

    printf("\n boundary conditions loaded \n");
}
void loadboundary2(double w)
{
    int ix, iy, iz, i;
    double dummy1;
    if ((streamw = fopen("allboundaries.dat", "r")) == NULL)
    {
        printf("\n Error ");
        exit(1);
    }
    iz = 0;
    for (iy = 0; iy < ny; iy++)
        for (ix = 0; ix < nx; ix++)
        {
            i = nynz * ix + nz * iy + iz;
            fscanf(streamw, "%lf", &dummy1);
            Bx[i] = Bx1[i] = (1.0 - w) * Bx[i] + w * dummy1;
            fscanf(streamw, "%lf", &dummy1);
            By[i] = By1[i] = (1.0 - w) * By[i] + w * dummy1;

            fscanf(streamw, "%lf", &dummy1);
            Bz[i] = Bz1[i] = (1.0 - w) * Bz[i] + w * dummy1;
        }
    fclose(streamw);
    /*
printf("\n boundary conditions updated, w=%lf \n",w);
*/
}
void loadvectormag()
{
    int ix, iy, iz, i;
    double dummy1;
    if ((streamw = fopen("allboundaries.dat", "r")) == NULL)
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
    // #define DUMP i=nynz*ix+nz*iy+iz;
    // fscanf(streamw,"%lf", &dummy1);
    // Bx[i]=dummy1;
    // fscanf(streamw,"%lf", &dummy1);
    // By[i]=dummy1;
    // fscanf(streamw,"%lf", &dummy1);
    // Bz[i]=dummy1;

    fclose(streamw);
    printf("\n Vectormagnetogram loaded \n");
}
void loadvectormag2()
{
    int ix, iy, iz, i;
    double dummy1;
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
            fscanf(streamw, "%lf", &dummy1);
            Bxorig[i] = dummy1;
            fscanf(streamw, "%lf", &dummy1);
            Byorig[i] = dummy1;
            fscanf(streamw, "%lf", &dummy1);
            Bzorig[i] = dummy1;
        }
    fclose(streamw);
    printf("\n Vectormagnetogram loaded in Bobs\n");
}
