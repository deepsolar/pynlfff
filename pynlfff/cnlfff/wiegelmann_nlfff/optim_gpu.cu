/*
 * @Description: https://doi.org/10.1007/s11207-012-9966-z
 * @Author: Thomas Wiegelmann (wiegelmann@mps.mpg.de)
 * @Date: 
 * @LastEditors: Xinze Zhang (zhangxinze17@mails.ucas.ac.cn)
 * @LastEditDescription: Update GPU version
 * @LastEditTime: 202212
*/

#include <stdio.h>
#include <time.h>

#define MCENTERGRAD(f, id) ((f[i + id] - f[i - id]) / doubled_h)
#define MLEFTGRAD(f, id) ((-3 * f[i] + 4 * f[i + id] - f[i + (id << 1)]) / doubled_h)
#define MRIGHTGRAD(f, id) ((+3 * f[i] - 4 * f[i - id] + f[i - (id << 1)]) / doubled_h)

/* GRAD for Boundaries , all 3 differences needed */
#define GRADX(f, i) ((ix > 0 && ix < nx - 1) ? (MCENTERGRAD(f, nynz)) : ((ix == 0) ? (MLEFTGRAD(f, nynz)) : ((ix == nx - 1) ? (MRIGHTGRAD(f, nynz)) : (0.0))))
#define GRADY(f, i) ((iy > 0 && iy < ny - 1) ? (MCENTERGRAD(f, nz)) : ((iy == 0) ? (MLEFTGRAD(f, nz)) : ((iy == ny - 1) ? (MRIGHTGRAD(f, nz)) : (0.0))))
#define GRADZ(f, i) ((iz > 0 && iz < nz - 1) ? (MCENTERGRAD(f, 1)) : ((iz == 0) ? (MLEFTGRAD(f, 1)) : ((iz == nz - 1) ? (MRIGHTGRAD(f, 1)) : (0.0))))

#define GRADX_INNER(f, i) (MCENTERGRAD(f, nynz))
#define GRADY_INNER(f, i) (MCENTERGRAD(f, nz))
#define GRADZ_INNER(f, i) (MCENTERGRAD(f, 1))

extern double time1_calculate, time2_calculate, timeTot_calculate;
extern double time1_calculate1, time2_calculate1, timeTot_calculate1;
extern double time1_calculate2, time2_calculate2, timeTot_calculate2;
extern double time1_calculate3, time2_calculate3, timeTot_calculate3;
extern double time1_calculate4, time2_calculate4, timeTot_calculate4;

__global__ void green_d(const int nx, const int ny, const int nz, const int cube_x, const int cube_y, const int cube_z, const double *x, const double *y, const double *z, const double *bz0, double *Pot0)
{
    int i, i2, ix, iy, iz, ix1, iy1, nynz = ny * nz;
    double dummy1, r, rx, ry, rz;

    int delta_x = threadIdx.x * cube_x;
    int delta_y = threadIdx.y * cube_y;
    int delta_z = blockIdx.z * cube_z;
    int max_x = (delta_x + cube_x);
    int max_y = (delta_y + cube_y);
    int max_z = (delta_z + cube_z);
    max_x = max_x < nx ? max_x : nx;
    max_y = max_y < ny ? max_y : ny;
    max_z = max_z < nz ? max_z : nz;

    for (ix = delta_x; ix < max_x; ix++)
        for (iy = delta_y; iy < max_y; iy++)
            for (iz = delta_z; iz < max_z; iz++)
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

void green_(double *Bx, double *By, double *Bz)
{
    FILE *streamw, *initfile;
    double zoff, dummy1, doubled_h;
    int nx, ny, nz, nynz, nxnynz;
    int i, i2, ix, iy, iz;
    doubled_h = 1.0 * 2;
    char leer[25];

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

    double *x, *y, *z, *bz0, *Pot0;
    x = (double *)calloc(nx, sizeof(double));
    y = (double *)calloc(ny, sizeof(double));
    z = (double *)calloc(nz, sizeof(double));
    bz0 = (double *)calloc(nx * ny, sizeof(double));
    Pot0 = (double *)calloc(nxnynz, sizeof(double));

    double *x_d, *y_d, *z_d, *bz0_d, *Pot0_d;
    cudaMalloc((void **)&x_d, nx * sizeof(double));
    cudaMalloc((void **)&y_d, ny * sizeof(double));
    cudaMalloc((void **)&z_d, nz * sizeof(double));
    cudaMalloc((void **)&bz0_d, nx * ny * sizeof(double));
    cudaMalloc((void **)&Pot0_d, nxnynz * sizeof(double));

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

    int cube_x, cube_y, cube_z, ncube_x, ncube_y, ncube_z;
    cube_x = (nx + 31) / 32;
    cube_y = (ny + 31) / 32;
    cube_z = (nz + 7) / 8;
    cube_x = cube_x < 4 ? 4 : cube_x;
    cube_y = cube_y < 4 ? 4 : cube_y;
    cube_z = cube_z < 4 ? 4 : cube_z;
    ncube_x = (nx + cube_x - 1) / cube_x;
    ncube_y = (ny + cube_y - 1) / cube_y;
    ncube_z = (nz + cube_z - 1) / cube_z;

    dim3 blockSize(ncube_x, ncube_y, 1);
    dim3 gridSize(1, 1, ncube_z);

    cudaMemcpy((void *)x_d, (void *)x, nx * sizeof(double), cudaMemcpyHostToDevice);
    cudaMemcpy((void *)y_d, (void *)y, ny * sizeof(double), cudaMemcpyHostToDevice);
    cudaMemcpy((void *)z_d, (void *)z, nz * sizeof(double), cudaMemcpyHostToDevice);
    cudaMemcpy((void *)bz0_d, (void *)bz0, nx * ny * sizeof(double), cudaMemcpyHostToDevice);
    cudaMemcpy((void *)Pot0_d, (void *)Pot0, nxnynz * sizeof(double), cudaMemcpyHostToDevice);

    green_d<<<gridSize, blockSize>>>(nx, ny, nz, cube_x, cube_y, cube_z, x_d, y_d, z_d, bz0_d, Pot0_d);

    cudaMemcpy((void *)Pot0, (void *)Pot0_d, nxnynz * sizeof(double), cudaMemcpyDeviceToHost);

    /* Write to Binary */
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

void green(double *Bx, double *By, double *Bz)
{
    FILE *streamw, *initfile;
    double zoff, dummy1, doubled_h, r, rx, ry, rz;
    int nx, ny, nz, nynz, nxnynz;
    int i, i2, /*i3,*/ ix, iy, iz, ix1, iy1;
    doubled_h = 1.0 * 2;
    char leer[25];

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

    double *x, *y, *z, *bz0, *Pot0;
    x = (double *)calloc(nx, sizeof(double));
    y = (double *)calloc(ny, sizeof(double));
    z = (double *)calloc(nz, sizeof(double));
    Pot0 = (double *)calloc(nxnynz, sizeof(double));
    bz0 = (double *)calloc(nx * ny, sizeof(double));

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

__global__ void sum1D_d(int nx, int slice_nx, double *x)
{
    int ix;
    int delta_x = threadIdx.x * slice_nx;
    int max_x = (delta_x + slice_nx);
    max_x = max_x < nx ? max_x : nx;

    for (ix = delta_x + 1; ix < max_x; ix++)
    {
        x[delta_x] += x[ix];
    }

    __syncthreads();
    if (threadIdx.x == 0)
    {
        for (ix = slice_nx; ix < nx; ix += slice_nx)
            x[0] += x[ix];
    }
}

// this func will change x_d
double sum1D(int nx, double *x_d)
{
    int slice_nx = (nx + 63) / 64;
    int nslice_x = (nx + slice_nx - 1) / slice_nx;

    dim3 blockSize(nslice_x, 1, 1);
    dim3 gridSize(1);
    double sum;

    sum1D_d<<<gridSize, blockSize>>>(nx, slice_nx, x_d);
    cudaError_t err = cudaGetLastError();
    if (err != cudaSuccess)
    {
        printf("[sum1D_d]: CUDA Error: %s\n", cudaGetErrorString(err));
    }

    cudaMemcpy((void *)&sum, (void *)x_d, 1 * sizeof(double), cudaMemcpyDeviceToHost);

    return sum;
}

__global__ void calculateL3_d(const int nx, const int ny, const int nz, const int rect_ny, double *help, const double *mask, const double *Bx, const double *By, const double *Bz, const double *Bxorig, const double *Byorig, const double *Bzorig)
{
    int nynz = ny * nz, i, i1, ix, iy = threadIdx.y;

    int delta_y = threadIdx.y * rect_ny;
    int max_y = (delta_y + rect_ny);
    max_y = max_y < ny ? max_y : ny;

    for (iy = delta_y; iy < max_y; iy++)
    {
        help[iy] = 0.0;
        for (ix = 0; ix < nx; ix++)
        {
            i = ix * nynz + iy * nz;
            i1 = ix * ny + iy;
            help[iy] = help[iy] + mask[i1] * ((Bx[i] - Bxorig[i1]) * (Bx[i] - Bxorig[i1]) + (By[i] - Byorig[i1]) * (By[i] - Byorig[i1]) + (Bz[i] - Bzorig[i1]) * (Bz[i] - Bzorig[i1]));
        }
    }

    __syncthreads();
    if (threadIdx.y == 0)
    {
        for (iy = 1; iy < ny; iy++)
            help[0] += help[iy];
    }
}

double calculateL3(int nx, int ny, int nz, double nave, double *help_d, const double *mask_d, const double *Bx_d, const double *By_d, const double *Bz_d, const double *Bxorig_d, const double *Byorig_d, const double *Bzorig_d)
{
    int rect_ny = (ny + 1023) / 1024;
    int nrect_y = (ny + rect_ny - 1) / rect_ny;

    dim3 blockSize(1, nrect_y, 1);
    dim3 gridSize(1);
    double L3 = 0.0;

    calculateL3_d<<<gridSize, blockSize>>>(nx, ny, nz, rect_ny, help_d, mask_d, Bx_d, By_d, Bz_d, Bxorig_d, Byorig_d, Bzorig_d);
    cudaMemcpy((void *)&L3, (void *)help_d, 1 * sizeof(double), cudaMemcpyDeviceToHost);
    L3 = L3 / nave;

    return L3;
}

__global__ void calculateL_d(const int *shape, const double doubled_h,
                             const double *Bx, const double *By, const double *Bz,
                             float *DivB, float *odotb, float *oxbx, float *oxby, float *oxbz,
                             float *oxjx, float *oxjy, float *oxjz, float *oxa, float *oya, float *oza, float *oxb, float *oyb, float *ozb,
                             double *helpLs)
{
    int nx = shape[0], ny = shape[1], nz = shape[2], cube_x = shape[3], cube_y = shape[4], cube_z = shape[5], ncube_x = shape[6], ncube_y = shape[7], ncube_z = shape[8];
    double bx, by, bz, cbx, cby, cbz, fx, fy, fz;
    double divB, b2;
    double helpL = 0.0, helpL1 = 0.0, helpL2 = 0.0;
    double o2a, o2b;
    int ix, iy, iz, i;
    int nynz = ny * nz;
    int icube = blockIdx.z * ncube_y * ncube_x + threadIdx.y * ncube_x + threadIdx.x;
    int ncube_xyz = ncube_z * ncube_y * ncube_x;
    int delta_x = threadIdx.x * cube_x;
    int delta_y = threadIdx.y * cube_y;
    int delta_z = blockIdx.z * cube_z;
    int max_x = (delta_x + cube_x);
    int max_y = (delta_y + cube_y);
    int max_z = (delta_z + cube_z);
    max_x = max_x < nx ? max_x : nx;
    max_y = max_y < ny ? max_y : ny;
    max_z = max_z < nz ? max_z : nz;

    for (ix = delta_x; ix < max_x; ix++)
        for (iy = delta_y; iy < max_y; iy++)
            for (iz = delta_z; iz < max_z; iz++)
            {
                i = ix * nynz + iy * nz + iz;
                bx = Bx[i];
                by = By[i];
                bz = Bz[i];

                b2 = (bx * bx + by * by + bz * bz);

                cbx = GRADY(Bz, i) - GRADZ(By, i);
                cby = GRADZ(Bx, i) - GRADX(Bz, i);
                cbz = GRADX(By, i) - GRADY(Bx, i);
                divB = GRADX(Bx, i) + GRADY(By, i) + GRADZ(Bz, i);

                DivB[i] = divB;

                fx = cby * bz - cbz * by;
                fy = cbz * bx - cbx * bz;
                fz = cbx * by - cby * bx;

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

                oxbx[i] = oya[i] * bz - oza[i] * by;
                oxby[i] = oza[i] * bx - oxa[i] * bz;
                oxbz[i] = oxa[i] * by - oya[i] * bx;
                odotb[i] = oxb[i] * bx + oyb[i] * by + ozb[i] * bz;
                oxjx[i] = oya[i] * cbz - oza[i] * cby;
                oxjy[i] = oza[i] * cbx - oxa[i] * cbz;
                oxjz[i] = oxa[i] * cby - oya[i] * cbx;
            }
    helpLs[icube] = helpL;
    helpLs[ncube_xyz + icube] = helpL1;
    helpLs[ncube_xyz * 2 + icube] = helpL2;
}

__global__ void update_d(const int *shape, const int calcb, const int boundary, const double doubled_h, const double oldL, const double L, const double Lx, const double nue,
                         const double *Bxorig, const double *Byorig, const double *Bzorig, const double *mask,
                         float *DivB, float *odotb, float *oxbx, float *oxby, float *oxbz,
                             float *oxjx, float *oxjy, float *oxjz, float *oxa, float *oya, float *oza, float *oxb, float *oyb, float *ozb,
                         double *mues, double *Bx, double *By, double *Bz, double *Bx1, double *By1, double *Bz1)
{
    int nx = shape[0], ny = shape[1], nz = shape[2], cube_x = shape[3], cube_y = shape[4], cube_z = shape[5];
    double mue = mues[0], mue2 = mues[1];

    int i, i1, ix, iy, iz;
    int nynz = ny * nz;
    int delta_x = threadIdx.x * cube_x;
    int delta_y = threadIdx.y * cube_y;
    int delta_z = blockIdx.z * cube_z;
    int max_x = (delta_x + cube_x);
    int max_y = (delta_y + cube_y);
    int max_z = (delta_z + cube_z);
    max_x = max_x < nx ? max_x : nx;
    max_y = max_y < ny ? max_y : ny;
    max_z = max_z < nz ? max_z : nz;

    float Fx,Fy,Fz;
    double o2a, o2b;
    double term1x, term2x, term3x, term4x, term5ax, term5bx;
    double term1y, term2y, term3y, term4y, term5ay, term5by;
    double term1z, term2z, term3z, term4z, term5az, term5bz;

    /*** L minimieren ***/
    for (ix = delta_x == 0 ? 1 : delta_x; ix < (max_x == nx ? nx - 1 : max_x); ix++)
        for (iy = delta_y == 0 ? 1 : delta_y; iy < (max_y == ny ? ny - 1 : max_y); iy++)
            for (iz = delta_z == 0 ? 1 : delta_z; iz < (max_z == nz ? nz - 1 : max_z); iz++)
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

                Fx = (term1x - term2x + term5ax) + (term3x - term4x + term5bx);
                Fy = (term1y - term2y + term5ay) + (term3y - term4y + term5by);
                Fz = (term1z - term2z + term5az) + (term3z - term4z + term5bz);

                Bx1[i] = Bx[i] + 1.0 * mue * Fx;
                By1[i] = By[i] + 1.0 * mue * Fy;
                Bz1[i] = Bz[i] + 1.0 * mue * Fz;
            }
    /*  Try to repair errors in Magnetogram */
    if (calcb == 40)
    {
        iz = 0;
        mue2 = mue;

        for (ix = delta_x; ix < max_x; ix++)
            for (iy = delta_y; iy < max_y; iy++)
            {
                i = ix * nynz + iy * nz + iz;
                i1 = ix * ny + iy;
                Bx1[i] = Bx[i] - 1.0 * mue2 * oxby[i] - nue * mask[i1] * (Bx[i] - Bxorig[i1]);
                By1[i] = By[i] + 1.0 * mue2 * oxbx[i] - nue * mask[i1] * (By[i] - Byorig[i1]);
                Bz1[i] = Bz[i] - nue * (Bz[i] - Bzorig[i1]);
            }
    }

    /* Use G to minmize L at the boundary */
    if ((calcb == 40) && (boundary == 1))
    {
        mue2 = mue / (1.0 * Lx) / 50.0;
        mue2 = mue;
        /* printf("\n Boundary-Relax "); */
        for (ix = delta_x; ix < max_x; ix++)
            for (iy = delta_y; iy < max_y; iy++)
            {
                iz = 0; /* bottom */
                i = ix * nynz + iy * nz + iz;
                iz = nz - 1; /*top */
                i = ix * nynz + iy * nz + iz;
                Bx1[i] = Bx[i] + mue2 * oxby[i];
                By1[i] = By[i] - mue2 * oxbx[i];
                Bz1[i] = 1.0 * (Bz[i] + mue2 * odotb[i]);
            }
        for (ix = delta_x; ix < max_x; ix++)
            for (iz = delta_z; iz < max_z; iz++)
            {
                iy = 0; /* front */
                i = ix * nynz + iy * nz + iz;
                Bx1[i] = Bx[i] + mue2 * oxbz[i];
                By1[i] = 1.0 * (By[i] - mue2 * odotb[i]);
                Bz1[i] = Bz[i] - mue2 * oxbx[i];
                iy = ny - 1; /* back */
                i = ix * nynz + iy * nz + iz;
                Bx1[i] = Bx[i] - mue2 * oxbz[i];
                By1[i] = 1.0 * (By[i] + mue2 * odotb[i]);
                Bz1[i] = Bz[i] + mue2 * oxbx[i];
            }
        for (iy = delta_y; iy < max_y; iy++)
            for (iz = delta_z; iz < max_z; iz++)
            {
                ix = 0; /* left */
                i = ix * nynz + iy * nz + iz;
                Bx1[i] = 1.0 * (Bx[i] - mue2 * odotb[i]);
                By1[i] = By[i] - mue2 * oxbz[i];
                Bz1[i] = Bz[i] + mue2 * oxby[i];
                ix = nx - 1; /* right */
                i = ix * nynz + iy * nz + iz;
                Bx1[i] = 1.0 * (Bx[i] + mue2 * odotb[i]);
                By1[i] = By[i] + mue2 * oxbz[i];
                Bz1[i] = Bz[i] - mue2 * oxby[i];
            }
    }
}

void calculate(const int maxit, const int diagstep, const int calcb, const int boundary, const int nx, const int ny, const int nz, const double dx, const double dy, const double dz, const double Lx, const double nave, const double nue,
               const double *Bxorig, const double *Byorig, const double *Bzorig, const double *mask,
               int &it, double &mue, FILE *streamw, double *Bx, double *By, double *Bz)
{
    int cube_x, cube_y, cube_z, ncube_x, ncube_y, ncube_z;
    cube_x = (nx + 32 - 1) / 32;
    cube_y = (ny + 32 - 1) / 32;
    cube_z = (nz + 32 - 1) / 32;
    cube_x = cube_x < 4 ? 4 : cube_x;
    cube_y = cube_y < 4 ? 4 : cube_y;
    cube_z = cube_z < 4 ? 4 : cube_z;
    ncube_x = (nx + cube_x - 1) / cube_x;
    ncube_y = (ny + cube_y - 1) / cube_y;
    ncube_z = (nz + cube_z - 1) / cube_z;

    int shape[9] = {nx, ny, nz, cube_x, cube_y, cube_z, ncube_x, ncube_y, ncube_z};
    int nxny = nx * ny, nxnynz = nx * ny * nz, statcount = 0, restore = 0;
    int ncube_xyz = ncube_x * ncube_y * ncube_z;
    double mue2, doubled_h = dx * 2, L1 = 0.0, L2 = 0.0, L3 = 0.0, L = 0.0, oldL = 0.0, prevL = 0.0, newL = 0.0, gradL = 0.0;
    double mues[2];

    dim3 blockSize(ncube_x, ncube_y, 1);
    dim3 gridSize(1, 1, ncube_z);

    int *shape_d;
    float *DivB_d, *odotb_d, *oxbx_d, *oxby_d, *oxbz_d, *oxjx_d, *oxjy_d, *oxjz_d, *oxa_d, *oya_d, *oza_d, *oxb_d, *oyb_d, *ozb_d;
    double *mues_d, *Bxorig_d, *Byorig_d, *Bzorig_d, *help_d, *Bx_d, *By_d, *Bz_d, *Bx1_d, *By1_d, *Bz1_d, *Bx_swap_d, *By_swap_d, *Bz_swap_d, *mask_d;

    cudaMalloc((void **)&shape_d, 9 * sizeof(int));
    cudaMalloc((void **)&DivB_d, nxnynz * sizeof(float));
    cudaMalloc((void **)&odotb_d, nxnynz * sizeof(float));
    cudaMalloc((void **)&oxbx_d, nxnynz * sizeof(float));
    cudaMalloc((void **)&oxby_d, nxnynz * sizeof(float));
    cudaMalloc((void **)&oxbz_d, nxnynz * sizeof(float));
    cudaMalloc((void **)&oxjx_d, nxnynz * sizeof(float));
    cudaMalloc((void **)&oxjy_d, nxnynz * sizeof(float));
    cudaMalloc((void **)&oxjz_d, nxnynz * sizeof(float));
    cudaMalloc((void **)&oxa_d, nxnynz * sizeof(float));
    cudaMalloc((void **)&oya_d, nxnynz * sizeof(float));
    cudaMalloc((void **)&oza_d, nxnynz * sizeof(float));
    cudaMalloc((void **)&oxb_d, nxnynz * sizeof(float));
    cudaMalloc((void **)&oyb_d, nxnynz * sizeof(float));
    cudaMalloc((void **)&ozb_d, nxnynz * sizeof(float));
    cudaMalloc((void **)&mues_d, 2 * sizeof(double));
    cudaMalloc((void **)&help_d, 3 * ncube_xyz * sizeof(double));
    cudaMalloc((void **)&Bx_d, nxnynz * sizeof(double));
    cudaMalloc((void **)&By_d, nxnynz * sizeof(double));
    cudaMalloc((void **)&Bz_d, nxnynz * sizeof(double));
    cudaMalloc((void **)&Bx1_d, nxnynz * sizeof(double));
    cudaMalloc((void **)&By1_d, nxnynz * sizeof(double));
    cudaMalloc((void **)&Bz1_d, nxnynz * sizeof(double));
    cudaMalloc((void **)&Bxorig_d, nxny * sizeof(double));
    cudaMalloc((void **)&Byorig_d, nxny * sizeof(double));
    cudaMalloc((void **)&Bzorig_d, nxny * sizeof(double));
    cudaMalloc((void **)&mask_d, nxny * sizeof(double));

    cudaMemset((float *)DivB_d, (float)0.0, nxnynz * sizeof(float));
    cudaMemcpy((void *)shape_d, (void *)shape, 9 * sizeof(int), cudaMemcpyHostToDevice);
    cudaMemcpy((void *)Bxorig_d, (void *)Bxorig, nxny * sizeof(double), cudaMemcpyHostToDevice);
    cudaMemcpy((void *)Byorig_d, (void *)Byorig, nxny * sizeof(double), cudaMemcpyHostToDevice);
    cudaMemcpy((void *)Bzorig_d, (void *)Bzorig, nxny * sizeof(double), cudaMemcpyHostToDevice);
    cudaMemcpy((void *)mask_d, (void *)mask, nxny * sizeof(double), cudaMemcpyHostToDevice);
    cudaMemcpy((void *)Bx_d, (void *)Bx, nxnynz * sizeof(double), cudaMemcpyHostToDevice);
    cudaMemcpy((void *)By_d, (void *)By, nxnynz * sizeof(double), cudaMemcpyHostToDevice);
    cudaMemcpy((void *)Bz_d, (void *)Bz, nxnynz * sizeof(double), cudaMemcpyHostToDevice);
    cudaMemcpy((void *)Bx1_d, (void *)Bx_d, nxnynz * sizeof(double), cudaMemcpyDeviceToDevice);
    cudaMemcpy((void *)By1_d, (void *)By_d, nxnynz * sizeof(double), cudaMemcpyDeviceToDevice);
    cudaMemcpy((void *)Bz1_d, (void *)Bz_d, nxnynz * sizeof(double), cudaMemcpyDeviceToDevice);

    time1_calculate = clock();
    cudaError_t err = cudaGetLastError();
    while (it < maxit && statcount < 10 && mue > 1.0e-7 * dx * dx)
    {
        it = it + 1;

        time1_calculate1 = clock();
        calculateL_d<<<gridSize, blockSize>>>(shape_d, doubled_h, Bx_d, By_d, Bz_d, DivB_d, odotb_d, oxbx_d, oxby_d, oxbz_d, oxjx_d, oxjy_d, oxjz_d, oxa_d, oya_d, oza_d, oxb_d, oyb_d, ozb_d, help_d);
        if (err != cudaSuccess)
        {
            printf("[calculateL_1_d]: CUDA Error: %s\n", cudaGetErrorString(err));
        }
        cudaDeviceSynchronize();
        time2_calculate1 = clock();
        timeTot_calculate1 += ((time2_calculate1 - time1_calculate1) / CLOCKS_PER_SEC);

        time1_calculate2 = clock();
        L = sum1D(ncube_xyz, help_d);
        L1 = sum1D(ncube_xyz, help_d + ncube_xyz);
        L2 = sum1D(ncube_xyz, help_d + ncube_xyz * 2);
        L = L * dx * dy * dz;
        L1 = L1 * dx * dy * dz;
        L2 = L2 * dx * dy * dz;
        time2_calculate2 = clock();
        timeTot_calculate2 += ((time2_calculate2 - time1_calculate2) / CLOCKS_PER_SEC);

        if (calcb == 40)
        {
            time1_calculate3 = clock();

            L3 = calculateL3(nx, ny, nz, nave, help_d, mask_d, Bx_d, By_d, Bz_d, Bxorig_d, Byorig_d, Bzorig_d);
            err = cudaGetLastError();
            if (err != cudaSuccess)
            {
                printf("[calculateL3]: CUDA Error: %s\n", cudaGetErrorString(err));
            }
            cudaDeviceSynchronize();
            L = L + L3;

            time2_calculate3 = clock();
            timeTot_calculate3 += ((time2_calculate3 - time1_calculate3) / CLOCKS_PER_SEC);
        }

        if (it == 0)
            oldL = L;

        if (restore == 1)
            L = oldL; /* restore when L is rejected */

        if (it > 0 && L > oldL) /* Changed L>=oldL to L>oldL */
        {
            restore = 1; /* restore in the next loop step */
            mue = mue / 2.0;
            printf("\n mue reduced, mue= %lf \t mue/dx^2= %lf", mue, mue / (dx * dx));
            printf("\n oldL= %lf \t L=%lf", oldL, L);
            it = it - 1;

            cudaMemcpy((void *)Bx_d, (void *)Bx1_d, nxnynz * sizeof(double), cudaMemcpyDeviceToDevice);
            cudaMemcpy((void *)By_d, (void *)By1_d, nxnynz * sizeof(double), cudaMemcpyDeviceToDevice);
            cudaMemcpy((void *)Bz_d, (void *)Bz1_d, nxnynz * sizeof(double), cudaMemcpyDeviceToDevice);
        }
        else
        {
            mue = mue * 1.01;
            restore = 0; /* no restore */
            oldL = L;
        }

        if (oldL >= L)
        {
            mues[0] = mue;
            mues[1] = mue2;
           
            time1_calculate4 = clock();
            
            cudaMemcpy((void *)mues_d, (void *)mues, 2 * sizeof(double), cudaMemcpyHostToDevice);
            update_d<<<gridSize, blockSize>>>(shape_d, calcb, boundary, doubled_h, oldL, L, Lx, nue, Bxorig_d, Byorig_d, Bzorig_d, mask_d, DivB_d, odotb_d, oxbx_d, oxby_d, oxbz_d, oxjx_d, oxjy_d, oxjz_d, oxa_d, oya_d, oza_d, oxb_d, oyb_d, ozb_d, mues_d, Bx_d, By_d, Bz_d, Bx1_d, By1_d, Bz1_d);
            cudaMemcpy((void *)mues, (void *)mues_d, 2 * sizeof(double), cudaMemcpyDeviceToHost);
            
            time2_calculate4 = clock();
            timeTot_calculate4 += ((time2_calculate4 - time1_calculate4) / CLOCKS_PER_SEC);
           
            Bx_swap_d = Bx_d;
            By_swap_d = By_d;
            Bz_swap_d = Bz_d;
            Bx_d = Bx1_d;
            By_d = By1_d;
            Bz_d = Bz1_d;
            Bx1_d = Bx_swap_d;
            By1_d = By_swap_d;
            Bz1_d = Bz_swap_d;
            mue = mues[0];
            mue2 = mues[1];
        }

        /*** Some tests with (Anti) Symmetric Boundary-conditions ***/
        if (it % diagstep == 0) /* && L<=oldL ) */
        {
            printf("\n %i L= %.4f", it, L);
            /* NEW: calc gradient (dL/dt)L for stopping rule */
            if (it == 0)
            {
                prevL = 2.0 * L;
                newL = L;
            }
            else
            {
                prevL = newL;
                newL = L;
            }
            gradL = fabs((newL - prevL) / newL);
            if (gradL < 0.0001)
            {
                statcount = statcount + 1;
                printf("\n *** STATIONARY STATE count: %i *** grad L/L= %lf \n", statcount, gradL);
            }
            if (gradL > 0.0001)
            {
                statcount = 0;
            }

            if (calcb != 40)
                printf(",  gradL/L= %lf", gradL);
            if (calcb == 40)
            {
                printf(",L1=%.4lf, L2=%.4lf,  L3= %.4lf", L1, L2, L3);
            }
            if ((streamw = fopen("step.log", "w")) == NULL)
            {
                printf("\n Error help.log");
                exit(1);
            }
            fprintf(streamw, "%i", it / diagstep);
            fclose(streamw);
            if ((streamw = fopen("prot.log", "a")) == NULL)
            {
                printf("\n Error prot.log");
                exit(1);
            }
            fprintf(streamw, "%lf \n %lf \n %lf \n %lf \n %lf \n %lf \n", 1.0 * it, L, gradL, L1, L2, L3);
            fclose(streamw);
        }
        /* End Diagnostik */
    }

    cudaMemcpy((void *)Bx, (void *)Bx_d, nxnynz * sizeof(double), cudaMemcpyDeviceToHost);
    cudaMemcpy((void *)By, (void *)By_d, nxnynz * sizeof(double), cudaMemcpyDeviceToHost);
    cudaMemcpy((void *)Bz, (void *)Bz_d, nxnynz * sizeof(double), cudaMemcpyDeviceToHost);

    cudaDeviceSynchronize();

    time2_calculate = clock();
    timeTot_calculate = (time2_calculate - time1_calculate) / CLOCKS_PER_SEC;
    // free();
    // cudaFree();
}
