/*
 * @Description: https://doi.org/10.1007/s11207-012-9966-z
 * @Author: Thomas Wiegelmann (wiegelmann@mps.mpg.de)
 * @Date: 
 * @LastEditors: Xinze Zhang (zhangxinze17@mails.ucas.ac.cn)
 * @LastEditDescription: Update GPU version
 * @LastEditTime: 202212
*/
/* Global Variables */
extern FILE *streamw, *initfile;
// extern double Cmn[102][102], lmn[102][102], rmn[102][102];
// extern double Lx, Ly, Lz, alpha, pi, q1;
//势场
extern int maxm, maxn;
extern double alpha, q1,pi,Lx, Ly;
extern double Cmn[maxm][maxn], lmn[maxm][maxn], rmn[maxm][maxn];
//extern double *Bx, *By, *Bz;
// extern double L1, L2, L3;
// extern double *t, *xt, *yt, *zt, *absB, *t2, *xyzB, *refB;
// extern double *x, *y, *z;
// extern double *Bx, *By, *Bz;
/* extern double *B; */
// extern double *Bx1, *By1, *Bz1, *Bx2, *By2, *Bz2;
// extern float *VxBx, *VxBy, *VxBz, *Rotvx, *Rotvy, *Rotvz;
// extern float *Jx, *Jy, *Jz, *Vx, *Vy, *Vz;
// extern float *Jx1, *Jy1, *Jz1;
// extern float *ox, *oy, *oz, *oxbx, *oxby, *oxbz, *odotb, *DivB;
// extern float *oxjx, *oxjy, *oxjz, *Fx, *Fy, *Fz;
/* double *Bxana, *Byana, *Bzana; */
// extern float *oxa, *oya, *oza, *oxb, *oyb, *ozb;
// extern double *Bxorig, *Byorig, *Bzorig, *mask;
// extern double *wa0, *wb0;
// extern float *wax, *way, *waz, *wbx, *wby, *wbz;
// extern double dt, length;
// extern double C;
// extern double dx, dy, dz, h;
// extern double mu0, rmu0, Ls, gausT, rmu0gausT, mue;
// extern int maxm, maxn;
// extern int maxsteps, max2;
// extern int nx, ny, nz, nynz, nxnynz, nd, nxmax, nymax, nzmax;
// extern int calcb, maxit, firsttime, m0, n0;
// extern int nxnynz1, nxnynz2, diagstep;
/* Parallelization */

/* Macros */

#define MCENTERGRAD(f, id) ((f[i + id] - f[i - id]) / (2 * h))
#define MLEFTGRAD(f, id) ((-3 * f[i] + 4 * f[i + id] - f[i + 2 * id]) / (2 * h))
#define MRIGHTGRAD(f, id) ((+3 * f[i] - 4 * f[i - id] + f[i - 2 * id]) / (2 * h))

/* GRAD for Boundaries , all 3 differences needed */
#define GRADX(f, i) ((ix > 0 && ix < nx - 1) ? (MCENTERGRAD(f, nynz)) : ((ix == 0) ? (MLEFTGRAD(f, nynz)) : ((ix == nx - 1) ? (MRIGHTGRAD(f, nynz)) : (0.0))))
#define GRADY(f, i) ((iy > 0 && iy < ny - 1) ? (MCENTERGRAD(f, nz)) : ((iy == 0) ? (MLEFTGRAD(f, nz)) : ((iy == ny - 1) ? (MRIGHTGRAD(f, nz)) : (0.0))))
#define GRADZ(f, i) ((iz > 0 && iz < nz - 1) ? (MCENTERGRAD(f, 1)) : ((iz == 0) ? (MLEFTGRAD(f, 1)) : ((iz == nz - 1) ? (MRIGHTGRAD(f, 1)) : (0.0))))
