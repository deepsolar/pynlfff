/*
 * @Description: https://doi.org/10.1007/s11207-012-9966-z
 * @Author: Thomas Wiegelmann (wiegelmann@mps.mpg.de)
 * @Date: 
 * @LastEditors: Xinze Zhang (zhangxinze17@mails.ucas.ac.cn)
 * @LastEditDescription: Update GPU version
 * @LastEditTime: 202212
*/

/* optimization.c */
/* Functions Omega and F from Wheatland-paper */
#include <stdio.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include "globals_gpu.h"

double calculateL(int &nx, int &ny, int &nz, int &nynz, int &nxnynz, int &nd, int &nxmax, int &nymax, int &nzmax,
                  double &dx, double &dy, double &dz, double &h, double &L1, double &L2, double &L3,
                  double *wa0, double *wb0, double *Bx, double *By, double *Bz,
                  float *Fx, float *Fy, float *Fz, float *DivB, float *odotb,
                  float *oxbx, float *oxby, float *oxbz, float *oxjx, float *oxjy, float *oxjz,
                  float *oxa, float *oya, float *oza, float *oxb, float *oyb, float *ozb,
                  float *wax, float *way, float *waz, float *wbx, float *wby, float *wbz)
{
    double bx, by, bz, cbx, cby, cbz, fx, fy, fz;
    double divB, b2, helpL, helpf, helpL1, helpL2;
    double o2a, o2b, term1x, term2x, term3x, term4x, term5ax, term5bx;
    double term1y, term2y, term3y, term4y, term5ay, term5by;
    double term1z, term2z, term3z, term4z, term5az, term5bz;
    double term6x, term6y, term6z, term7x, term7y, term7z;
    double dummy1, dummy2, dummy3, dummy4, dummy5, dummy6;
    int ix, iy, iz, i;
    int zaehl;

    h = dx;
    helpL = helpL1 = helpL2 = 0.0;
    helpf = 0.0;
    zaehl = 0;

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

                oxbx[i] = oya[i] * bz - oza[i] * by;
                oxby[i] = oza[i] * bx - oxa[i] * bz;
                oxbz[i] = oxa[i] * by - oya[i] * bx;
                odotb[i] = oxb[i] * bx + oyb[i] * by + ozb[i] * bz;
                oxjx[i] = oya[i] * cbz - oza[i] * cby;
                oxjy[i] = oza[i] * cbx - oxa[i] * cbz;
                oxjz[i] = oxa[i] * cby - oya[i] * cbx;
            }

    /***********************************************************************/
    helpL = helpL * dx * dy * dz;
    L1 = helpL1 * dx * dy * dz;
    L2 = helpL2 * dx * dy * dz;
    dummy1 = dummy2 = dummy3 = dummy4 = dummy5 = dummy6 = 0.0;

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
