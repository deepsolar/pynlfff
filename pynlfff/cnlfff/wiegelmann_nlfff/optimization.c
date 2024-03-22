/*
 * @Description: https://doi.org/10.1007/s11207-012-9966-z
 * @Author: Thomas Wiegelmann (wiegelmann@mps.mpg.de)
 * @Date: 
 * @LastEditors: Thomas Wiegelmann (wiegelmann@mps.mpg.de)
 * @LastEditTime: 
*/

/* optimization.c */
/* Functions Omega and F from Wheatland-paper */
#include <stdio.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include "globals.h"
#ifdef _OPENMP
#include <omp.h>
#endif
/*
double gradx(double *f, int i);
double grady(double *f, int i);
double gradz(double *f, int i);
*/
double calculateL()
{
    double bx, by, bz, cbx, cby, cbz, fx, fy, fz;
    double divB, b2, helpL, helpf, helpL1, helpL2;
    double o2a, o2b, term1x, term2x, term3x, term4x, term5ax, term5bx;
    double term1y, term2y, term3y, term4y, term5ay, term5by;
    double term1z, term2z, term3z, term4z, term5az, term5bz;
    double term6x, term6y, term6z, term7x, term7y, term7z;
    /* double dummy; */
    double dummy1, dummy2, dummy3, dummy4, dummy5, dummy6; /*dummy7; */ /*10.07.02 diagnostik */
    int ix, iy, iz, i;
    int zaehl;

    h = dx;
    helpL = helpL1 = helpL2 = 0.0;
    helpf = 0.0;
    zaehl = 0;
#ifdef _OPENMP
#pragma omp parallel for private(i, ix, iy, iz, bx, by, bz, cby, cbz, fx, fy, fz, divB, b2) reduction(+ \
                                                                                                      : helpL)
#endif
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
                    if (1 == 1) /* Read u=-grad p-rho grad psi */
                    {
                        oxa[i] = oxa[i]; /* +ux[i]/b2; */
                        oya[i] = oya[i]; /* +uy[i]/b2; */
                        oza[i] = oza[i]; /* +uz[i]/b2; */
                    }

                    o2a = oxa[i] * oxa[i] + oya[i] * oya[i] + oza[i] * oza[i];
                    o2b = oxb[i] * oxb[i] + oyb[i] * oyb[i] + ozb[i] * ozb[i];
                    helpL = helpL + wa0[i] * b2 * o2a + wb0[i] * b2 * o2b;
                    helpL1 = helpL1 + wa0[i] * b2 * o2a;
                    helpL2 = helpL2 + wb0[i] * b2 * o2b;
                }
                /*
else
{zaehl=zaehl+1;}
*/
                oxbx[i] = oya[i] * bz - oza[i] * by;
                oxby[i] = oza[i] * bx - oxa[i] * bz;
                oxbz[i] = oxa[i] * by - oya[i] * bx;
                odotb[i] = oxb[i] * bx + oyb[i] * by + ozb[i] * bz;
                oxjx[i] = oya[i] * cbz - oza[i] * cby;
                oxjy[i] = oza[i] * cbx - oxa[i] * cbz;
                oxjz[i] = oxa[i] * cby - oya[i] * cbx;
            }

    /***********************************************************************/
    /* helpL=gausT*gausT*helpL*dx*dy*dz; */
    helpL = helpL * dx * dy * dz;
    L1 = helpL1 * dx * dy * dz;
    L2 = helpL2 * dx * dy * dz;
    /*10.07.02 diagnostik */
    dummy1 = dummy2 = dummy3 = dummy4 = dummy5 = dummy6 = 0.0;
#ifdef _OPENMP
#pragma omp parallel for private(i, ix, iy, iz, o2a, o2b, term1x, term2x, term3x, term4x, term5ax, term5bx, term1y, term2y, term3y, term4y, term5ay, term5by, term1z, term2z, term3z, term4z, term5az, term5bz, term6x, term6y, term6z, term7x, term7y, term7z) reduction(+                                                                                                     \
                                                                                                                                                                                                                                                                          : dummy1) reduction(+                                                                                 \
                                                                                                                                                                                                                                                                                              : dummy2) reduction(+                                                             \
                                                                                                                                                                                                                                                                                                                  : dummy3) reduction(+                                         \
                                                                                                                                                                                                                                                                                                                                      : dummy4) reduction(+                     \
                                                                                                                                                                                                                                                                                                                                                          : dummy5) reduction(+ \
                                                                                                                                                                                                                                                                                                                                                                              : dummy6)
#endif
    for (ix = 0; ix < nx; ix++)
        for (iy = 0; iy < ny; iy++)
            for (iz = 0; iz < nz; iz++)
            {
                i = ix * nynz + iy * nz + iz;
                term1x = GRADY(oxbz, i) - GRADZ(oxby, i);
                term1y = GRADZ(oxbx, i) - GRADX(oxbz, i);
                term1z = GRADX(oxby, i) - GRADY(oxbx, i);

                term2x = oxjx[i];
                term2y = oxjy[i];
                term2z = oxjz[i];

                term3x = GRADX(odotb, i);
                term3y = GRADY(odotb, i);
                term3z = GRADZ(odotb, i);

                term4x = oxb[i] * DivB[i];
                term4y = oyb[i] * DivB[i];
                term4z = ozb[i] * DivB[i];

                o2a = oxa[i] * oxa[i] + oya[i] * oya[i] + oza[i] * oza[i];
                o2b = oxb[i] * oxb[i] + oyb[i] * oyb[i] + ozb[i] * ozb[i];
                term5ax = Bx[i] * o2a;
                term5ay = By[i] * o2a;
                term5az = Bz[i] * o2a;
                term5bx = Bx[i] * o2b;
                term5by = By[i] * o2b;
                term5bz = Bz[i] * o2b;
                /*
Fx[i]=(term1x-term2x+term3x-term4x+term5x);
Fy[i]=(term1y-term2y+term3y-term4y+term5y);
Fz[i]=(term1z-term2z+term3z-term4z+term5z);
*/
                /* Terms regarding weighting  function */
                term6x = oxby[i] * waz[i] - oxbz[i] * way[i];
                term6y = oxbz[i] * wax[i] - oxbx[i] * waz[i];
                term6z = oxbx[i] * way[i] - oxby[i] * wax[i];
                term7x = odotb[i] * wbx[i];
                term7y = odotb[i] * wby[i];
                term7z = odotb[i] * wbz[i];

                Fx[i] = wa0[i] * (term1x - term2x + term5ax) + wb0[i] * (term3x - term4x + term5bx) + term6x + term7x;
                Fy[i] = wa0[i] * (term1y - term2y + term5ay) + wb0[i] * (term3y - term4y + term5by) + term6y + term7y;
                Fz[i] = wa0[i] * (term1z - term2z + term5az) + wb0[i] * (term3z - term4z + term5bz) + term6z + term7z;
            }
    return helpL;
}
/*******************************************************************************************************/
double calculateLi() /* only inner Box */
{
    double bx, by, bz;            /* cbx; */
    double /* divB, */ b2, helpL; /* helpf; */
    double o2a, o2b, o2;
    int ix, iy, iz, i;

    h = dx;
    helpL = 0.0;
#ifdef _OPENMP
#pragma omp parallel for private(i, ix, iy, iz, bx, by, bz, b2) reduction(+ \
                                                                          : helpL)
#endif
    for (ix = nd; ix < nx - nd; ix++)
        for (iy = nd; iy < ny - nd; iy++)
            for (iz = 0; iz < nz - nd; iz++)
            {
                i = ix * nynz + iy * nz + iz;
                bx = Bx[i];
                by = By[i];
                bz = Bz[i];
                b2 = (bx * bx + by * by + bz * bz);
                o2a = oxa[i] * oxa[i] + oya[i] * oya[i] + oza[i] * oza[i];
                o2b = oxb[i] * oxb[i] + oyb[i] * oyb[i] + ozb[i] * ozb[i];
                o2 = o2a + o2b;

                helpL = helpL + b2 * o2;
            }

    helpL = helpL * dx * dy * dz;
    return helpL;
}
