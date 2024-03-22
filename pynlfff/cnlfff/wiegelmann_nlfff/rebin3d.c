/*
 * @Description: https://doi.org/10.1007/s11207-012-9966-z
 * @Author: Thomas Wiegelmann (wiegelmann@mps.mpg.de)
 * @Date: 
 * @LastEditors: Thomas Wiegelmann (wiegelmann@mps.mpg.de)
 * @LastEditTime: 
*/
/* rebin3d.c */
#include <stdio.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
//
main(int argc, char *argv[])
{
	FILE *streamw, *initfile;
	double *x, *y, *z;
	double *Bx, *By, *Bz, *B;
	double *Bx2, *By2, *Bz2, *B2;
	char leer[5];
	double dummy;
	int nx, ny, nz, nynz, nxnynz, nxny;
	int i, ix, iy, iz;
	int ix2, iy2, iz2;
	int ix3, iy3, iz3;
	int i1, i2, i3, i4, i5;

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
	fclose(initfile);

	/* Reduce nx,ny,nz to load smaller box */
	nx = nx / 2;
	ny = ny / 2;
	nz = nz / 2;
	nynz = ny * nz;
	nxnynz = nx * ny * nz;
	nxny = nx * ny;

	/* Allocate memory */
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

	/* Rebin to double grid */
	printf("\n Starting to expand grid");
	Bx2 = (double *)calloc(8 * nxnynz, sizeof(double));
	By2 = (double *)calloc(8 * nxnynz, sizeof(double));
	Bz2 = (double *)calloc(8 * nxnynz, sizeof(double));
	/* B2 = (double *) calloc(8*3*nxnynz, sizeof(double)); */

	/************************************/
	/*__start of corrected part__*/
	/***********************************/
	/* Write values of input field to corresponding places in coarser output field*/
	/*
	for(ix=0;ix<nx;ix++)
	for(iy=0;iy<ny;iy++)
	for(iz=0;iz<nz;iz++)
	*/
	for (ix2 = 0; ix2 < 2 * nx; ix2++)
		for (iy2 = 0; iy2 < 2 * ny; iy2++)
			for (iz2 = 0; iz2 < 2 * nz; iz2++)
			{
				ix = ix2 / 2;
				iy = iy2 / 2;
				iz = iz2 / 2;
				i = ix * nynz + iy * nz + iz;
				i1 = ix2 * 4 * nynz + iy2 * 2 * nz + iz2;
				if (ix2 % 2 == 0 && iy2 % 2 == 0 && iz2 % 2 == 0)
				{
					Bx2[i1] = Bx[i];
					By2[i1] = By[i];
					Bz2[i1] = Bz[i];
				}
			}
	/* From now on we interpolate only on the rebinned grid (smaller field is not used anymore)*/
	/* Interpolation in x- and y-direction for each height z */
	for (ix2 = 0; ix2 < (2 * nx) - 1; ix2++)
		for (iy2 = 0; iy2 < (2 * ny) - 1; iy2++)
			for (iz2 = 0; iz2 < (2 * nz) - 1; iz2++)
			{
				i1 = ix2 * 4 * nynz + iy2 * 2 * nz + iz2;
				/* linear interpolation in x-direction for each height z*/
				if (iy2 % 2 == 0 && ix2 % 2 != 0)
				{
					i2 = (ix2 + 1) * 4 * nynz + iy2 * 2 * nz + iz2;
					i3 = (ix2 - 1) * 4 * nynz + iy2 * 2 * nz + iz2;
					Bx2[i1] = 0.5 * (Bx2[i2] + Bx2[i3]);
					By2[i1] = 0.5 * (By2[i2] + By2[i3]);
					Bz2[i1] = 0.5 * (Bz2[i2] + Bz2[i3]);
				}
				/* linear interpolation in y-direction for each height z*/
				else if (iy2 % 2 != 0 && ix2 % 2 == 0)
				{
					i2 = ix2 * 4 * nynz + (iy2 + 1) * 2 * nz + iz2;
					i3 = ix2 * 4 * nynz + (iy2 - 1) * 2 * nz + iz2;
					Bx2[i1] = 0.5 * (Bx2[i2] + Bx2[i3]);
					By2[i1] = 0.5 * (By2[i2] + By2[i3]);
					Bz2[i1] = 0.5 * (Bz2[i2] + Bz2[i3]);
				}
				/* bilinear interpolation in x- and y-direction wherever linear interpolation is not possible*/
				/* due to not yet calculated values*/
				else if (iy2 % 2 != 0 && ix2 % 2 != 0)
				{
					i2 = (ix2 + 1) * 4 * nynz + (iy2 - 1) * 2 * nz + iz2;
					i3 = (ix2 - 1) * 4 * nynz + (iy2 - 1) * 2 * nz + iz2;
					i4 = (ix2 + 1) * 4 * nynz + (iy2 + 1) * 2 * nz + iz2;
					i5 = (ix2 - 1) * 4 * nynz + (iy2 + 1) * 2 * nz + iz2;
					Bx2[i1] = 0.25 * (Bx2[i2] + Bx2[i3] + Bx2[i4] + Bx2[i5]);
					By2[i1] = 0.25 * (By2[i2] + By2[i3] + By2[i4] + By2[i5]);
					Bz2[i1] = 0.25 * (Bz2[i2] + Bz2[i3] + Bz2[i4] + Bz2[i5]);
				}
			}
	/* Linear interpolation in z-direction based on previously calculated (x,y)-values*/
	for (iz2 = 0; iz2 < (2 * nz) - 1; iz2++)
	{
		if (iz2 % 2 != 0)
		{
			for (iy2 = 0; iy2 < (2 * ny) - 1; iy2++)
				for (ix2 = 0; ix2 < (2 * nx) - 1; ix2++)
				{
					i1 = ix2 * 4 * nynz + iy2 * 2 * nz + iz2;
					i2 = ix2 * 4 * nynz + iy2 * 2 * nz + (iz2 + 1);
					i3 = ix2 * 4 * nynz + iy2 * 2 * nz + (iz2 - 1);
					Bx2[i1] = 0.5 * (Bx2[i2] + Bx2[i3]);
					By2[i1] = 0.5 * (By2[i2] + By2[i3]);
					Bz2[i1] = 0.5 * (Bz2[i2] + Bz2[i3]);
				}
		}
	}
	/* Dublicate the n-1 elements of the input array to get the nth element of the output*/
	/* array because their interpolates would lie outside the input array*/
	for (ix2 = 0; ix2 < 2 * nx; ix2++)
		for (iy2 = 0; iy2 < 2 * ny; iy2++)
			for (iz2 = 0; iz2 < 2 * nz; iz2++)
			{
				i1 = ix2 * 4 * nynz + iy2 * 2 * nz + iz2;
				if (ix2 == (2 * nx) - 1)
				{
					i2 = (ix2 - 1) * 4 * nynz + iy2 * 2 * nz + iz2;
					Bx2[i1] = Bx2[i2];
					By2[i1] = By2[i2];
					Bz2[i1] = Bz2[i2];
				}
				else if (iy2 == (2 * ny) - 1)
				{
					i2 = ix2 * 4 * nynz + (iy2 - 1) * 2 * nz + iz2;
					Bx2[i1] = Bx2[i2];
					By2[i1] = By2[i2];
					Bz2[i1] = Bz2[i2];
				}
				else if (iz2 == (2 * nz) - 1)
				{
					i2 = ix2 * 4 * nynz + iy2 * 2 * nz + (iz2 - 1);
					Bx2[i1] = Bx2[i2];
					By2[i1] = By2[i2];
					Bz2[i1] = Bz2[i2];
				}
			}
	/*__end of corrected part__*/
	/* Output bin */
	if ((streamw = fopen(argv[2], "wb")) == NULL)
	{
		printf("\n Error Brebin.bin");
		exit(1);
	}
	fwrite(Bx2, sizeof(double) * 8 * nxnynz, 1, streamw);
	fwrite(By2, sizeof(double) * 8 * nxnynz, 1, streamw);
	fwrite(Bz2, sizeof(double) * 8 * nxnynz, 1, streamw);
	fclose(streamw);

	printf("\n\n Rebinned B written to %s done ", argv[2]);
	printf("\n\n rebin3d.c: End of program \n");

	/* Free previously allocated memory*/
	free(Bx);
	free(By);
	free(Bz);
	free(Bx2);
	free(By2);
	free(Bz2);
}
