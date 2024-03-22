/*
 * @Description: https://doi.org/10.1007/s11207-012-9966-z
 * @Author: Thomas Wiegelmann (wiegelmann@mps.mpg.de)
 * @Date: 
 * @LastEditors: Thomas Wiegelmann (wiegelmann@mps.mpg.de)
 * @LastEditTime: 
*/

/* fftpot4.c */
/* Use Allissandrakis linear force-free method, use FFT  */

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>

#ifdef _OPENMP
#include <omp.h>
#endif
#define PI 3.14159265358979323846
#define SWAP(a, b) \
  tempr = (a);     \
  (a) = (b);       \
  (b) = tempr

int convert2n2box()
{
  FILE *initfile, *streamw;
  char leer[25];
  int nx, ny, nz, nxny, i, i2, n, ix, iy, ix2, iy2, iz, i3;
  int nxnynz, nynz;
  int power, ip, nx2, ny2, nxny2, xoff, yoff;
  double dummy1;
  double dummy, time, alpha, relflux, totflux;
  double *Bz0, *Bz02, *Bzorig;
  float *fu2d;
  double *z, *kx, *ky, *kz2, *k;
  float *iphihat0, *iphihat, *fbx, *fby, *fbz;
  double *Bx, *By, *Bz;

  printf("\n Make Magnetogram power of 2 for FFT potential field");

  if ((initfile = fopen("grid.ini", "r")) == NULL)
  {
    printf("\n Error grid.ini");
    exit(1);
  }
  fscanf(initfile, "%s %i", &leer, &nx);
  fscanf(initfile, "%s %i", &leer, &ny);
  fscanf(initfile, "%s %i", &leer, &nz);
  fclose(initfile);
  nxny = nx * ny;
  printf("\n nx= %i, \t ny= %i, \t nz= %i", nx, ny, nz);
  Bz0 = (double *)calloc(nxny, sizeof(double));
  Bzorig = (double *)calloc(2 * nxny, sizeof(double)); /* Define as complex Field, maybe change later  */
  if ((initfile = fopen("allboundaries.dat", "r")) == NULL)
  {
    printf("\n Error allboundaries.dat ");
    exit(1);
  }
  for (iy = 0; iy < ny; iy++)
    for (ix = 0; ix < nx; ix++)
    {
      i = ny * ix + iy;
      i2 = 2 * i; /* for complex fields */
      fscanf(initfile, "%lf", &dummy);
      fscanf(initfile, "%lf", &dummy);
      fscanf(initfile, "%lf", &dummy);
      /* Bzorig[i2]=dummy;
Bzorig[i2+1]=0.0; */
      Bz0[i] = dummy;
    }
  fclose(initfile);
  printf("\n Bzorig loaded from Vectormagnetogram");

  /**********************************************************************************/
  /************ Write to files of power of 2  ***************************************/
  /**********************************************************************************/
  nx2 = ny2 = 0;
  power = 1;
  for (ip = 1; ip < 20; ip++)
  {
    power = power * 2;
    /* printf("\n %i, %i",ip,power); */
    if (nx <= power)
    {
      nx2 = power;
      break;
    }
  }
  power = 1;
  for (ip = 1; ip < 16; ip++)
  {
    power = power * 2;
    /* printf("\n %i, %i",ip,power); */
    if (ny <= power)
    {
      ny2 = power;
      break;
    }
  }
  printf("\n\n nx2= %i, \t ny2= %i", nx2, ny2);
  xoff = (nx2 - nx) / 2;
  yoff = (ny2 - ny) / 2;
  printf("\n X-offset= %i, \t Y-offset= %i", xoff, yoff);
  nxny2 = nx2 * ny2;
  if ((initfile = fopen("grid2n2.ini", "w")) == NULL)
  {
    printf("\n Error grid.ini");
    exit(1);
  }
  fprintf(initfile, "%s \n\t %i", "nx", nx2);
  fprintf(initfile, "\n%s \n\t %i", "ny", ny2);
  fprintf(initfile, "\n%s \n\t %i", "nz", nz);
  fprintf(initfile, "\n%s \n\t %i", "xoffset", xoff);
  fprintf(initfile, "\n%s \n\t %i", "yoffset", yoff);
  fclose(initfile);
  /* Now put in larger file, fill with zeros */
  Bz02 = (double *)calloc(nxny2, sizeof(double));

  for (iy = 0; iy < ny2; iy++)
    for (ix = 0; ix < nx2; ix++)
    {
      ix2 = ix + xoff;
      iy2 = iy + yoff;
      i2 = ny2 * ix2 + iy2;
      i = ny * ix + iy;
      if ((ix < nx) && (iy < ny))
      {
        Bz02[i2] = Bz0[i];
      }
    }
  if ((streamw = fopen("zboundaries2n2.dat", "w")) == NULL)
  {
    printf("\n Error zboundaries2n2.dat ");
    exit(1);
  }
  for (iy = 0; iy < ny2; iy++)
    for (ix = 0; ix < nx2; ix++)
    {
      i2 = ny2 * ix + iy;
      dummy1 = Bz02[i2];
      fprintf(streamw, "%lf\n", dummy1);
    }
  fclose(streamw);
  printf("\n zboundaries2n2.dat saved \n");

  /* printf("\n End of program \n"); */
}

void FFT(float data[], unsigned long nn, int isign)
/* Replaces data[1..2*nn] by its discrete Fourier transform, if isign is input as 1;
or replaces data[1..2*nn] by nn times its inverse discrete Fourier transform, if
isign is input as -1. data is a complex array of length nn or, equivalently, a real
array of length 2*nn. nn MUST be an integer power of 2 (this is not checked for!).
*/
{
  unsigned long n, mmax, m, j, istep, i, k;
  double wtemp, wr, wpr, wpi, wi, theta;
  float tempr, tempi;

  n = nn << 1;
  /*
  printf("\n nn= %i \t n= %i",nn,n);
  Diagnostik
for(k=0;k<nn;k++)
{printf("\n (%lf \t %lf)", data[2*k],data[2*k+1]);}
printf("\n");
*/

  j = 1;
  for (i = 1; i < n; i += 2)
  {
    if (j > i)
    {
      SWAP(data[j], data[i]);
      SWAP(data[j + 1], data[i + 1]);
    }

    m = n >> 1;
    while (m >= 2 && j > m)
    {
      j -= m;
      m >>= 1;
    }
    j += m;
  }

  /* Diagnostik
for(k=0;k<nn;k++)
{printf("\n (%lf \t %lf)", data[2*k],data[2*k+1]);}
*/
  /*  Danielson-Lanczos section */
  mmax = 2;
  while (n > mmax)
  { /*Outer loop executed log2 nn times. */
    istep = mmax << 1;
    theta = isign * (6.28318530717959 / mmax); /*Initialize the trigonometric recurrence.*/
    wtemp = sin(0.5 * theta);
    wpr = -2.0 * wtemp * wtemp;

    wpi = sin(theta);
    wr = 1.0;
    wi = 0.0;
    for (m = 1; m < mmax; m += 2)
    { /* Here are the two nested inner loops. */
      for (i = m; i <= n; i += istep)
      {
        j = i + mmax; /* This is the Danielson-Lanczos formula: */
        tempr = wr * data[j] - wi * data[j + 1];
        tempi = wr * data[j + 1] + wi * data[j];
        data[j] = data[i] - tempr;
        data[j + 1] = data[i + 1] - tempi;
        data[i] += tempr;
        data[i + 1] += tempi;
      }
      wr = (wtemp = wr) * wpr - wi * wpi + wr; /* Trigonometric recurrence. */
      wi = wi * wpr + wtemp * wpi + wi;
    }
    mmax = istep;
  }

  if (isign == -1)
  {
    for (k = 1; k < n + 1; k++)
    {
      data[k] = data[k] / nn;
    }
  }
}

/********************************************************************************/
/* Define 2D FT as a function by using 1D  FFT */
/***************** Main *********************************************************/
void DFT2D(float fu2d[], int nx, int ny, int isign)
{
  int i, i2, ix, iy, ix2, iy2;
  float *fx, *fy;
  fx = (float *)calloc(2 * nx, sizeof(float));
  fy = (float *)calloc(2 * ny, sizeof(float));

  /* Fourier transform first in x-direction */
  for (iy = 0; iy < ny; iy++)
  {
    for (ix = 0; ix < nx; ix++)
    {
      ix2 = 2 * ix;
      i = ny * ix + iy;
      i2 = 2 * i;
      fx[ix2] = fu2d[i2];
      fx[ix2 + 1] = fu2d[i2 + 1];
    }
    /* DFT1D(fx,fu,nx,isign); */
    FFT(fx - 1, nx, isign);

    for (ix = 0; ix < nx; ix++)
    {
      ix2 = 2 * ix;
      i = ny * ix + iy;
      i2 = 2 * i;
      fu2d[i2] = fx[ix2];
      fu2d[i2 + 1] = fx[ix2 + 1];
    }
  }
  /* Fourier transform in y-direction */
  for (ix = 0; ix < nx; ix++)
  {
    for (iy = 0; iy < ny; iy++)
    {
      iy2 = 2 * iy;
      i = ny * ix + iy;
      i2 = 2 * i;
      fy[iy2] = fu2d[i2];
      fy[iy2 + 1] = fu2d[i2 + 1];
    }
    /* DFT1D(fy,fu2,nx,isign); */
    FFT(fy - 1, ny, isign);
    for (iy = 0; iy < ny; iy++)
    {
      iy2 = 2 * iy;
      i = ny * ix + iy;
      i2 = 2 * i;
      fu2d[i2] = fy[iy2];
      fu2d[i2 + 1] = fy[iy2 + 1];
    }
  }
  free(fx);
  free(fy);
}
double zeit(void)
{
  static double tima = 0.;
  double tim, t;
  tim = (double)clock() / CLOCKS_PER_SEC;
  t = tim - tima;
  tima = tim;
  return (t);
}

/********************************************************************************/
/******************** Main ******************************************************/
/********************************************************************************/
int main()
{
  FILE *initfile;
  char leer[25];
  int nx, ny, nz, nxny, i, i2, n, ix, iy, ix2, iy2, iz, i3;
  int nxnynz, nynz, xoff, yoff;
  int nx2, ny2, nxny2, nynz2;
  double dummy, time, alpha, relflux, totflux;
  double *Bzorig;
  float *fu2d;
  double *z, *kx, *ky, *kz2, *k;
  float *iphihat0, *iphihat, *fbx, *fby, *fbz;
  double *Bx, *By, *Bz;
  double *oBx, *oBy, *oBz;
  convert2n2box();
  printf("\n Compute Potential field with Fourier Transform");
  time = zeit();

  if ((initfile = fopen("grid2n2.ini", "r")) == NULL)
  {
    printf("\n Error grid2n2.ini");
    exit(1);
  }
  fscanf(initfile, "%s %i", &leer, &nx);
  fscanf(initfile, "%s %i", &leer, &ny);
  fscanf(initfile, "%s %i", &leer, &nz);
  fscanf(initfile, "%s %i", &leer, &xoff);
  fscanf(initfile, "%s %i", &leer, &yoff);
  fclose(initfile);
  nxny = nx * ny;
  printf("\n nx= %i, \t ny= %i, \t nz= %i", nx, ny, nz);

  Bzorig = (double *)calloc(2 * nxny, sizeof(double)); /* Define as complex Field, maybe change later  */
  if ((initfile = fopen("zboundaries2n2.dat", "r")) == NULL)
  {
    printf("\n Error zboundaries2n2.dat ");
    exit(1);
  }
  for (iy = 0; iy < ny; iy++)
    for (ix = 0; ix < nx; ix++)
    {
      i = ny * ix + iy;
      i2 = 2 * i; /* for complex fields */
      fscanf(initfile, "%lf", &dummy);
      /*fscanf(initfile,"%lf", &dummy);
fscanf(initfile,"%lf", &dummy);*/
      Bzorig[i2] = dummy;
      Bzorig[i2 + 1] = 0.0;
    }
  fclose(initfile);
  printf("\n Bzorig loaded from Vectormagnetogram");
  /* Check flux balance */
  relflux = totflux = 0.0;
  for (iy = 0; iy < ny; iy++)
    for (ix = 0; ix < nx; ix++)
    {
      i = ny * ix + iy;
      i2 = 2 * i;
      relflux = relflux + Bzorig[i2];
      totflux = totflux + fabs(Bzorig[i2]);
      /* totflux=totflux+sqrt(Bzorig[i2]*Bzorig[i2]); */
    }
  printf("\n\n ********** Mark *********");
  printf("\n Flux Balance: %lf", relflux / totflux);

  /* Fourier transform in 2D */

  fu2d = (float *)calloc(2 * nxny, sizeof(float));
  for (iy = 0; iy < ny; iy++)
    for (ix = 0; ix < nx; ix++)
    {
      i = ny * ix + iy;
      i2 = 2 * i;
      fu2d[i2] = Bzorig[i2];
      fu2d[i2 + 1] = Bzorig[i2 + 1];
    }
  DFT2D(fu2d, nx, ny, -1);

  /*
for(ix=0;ix<nx;ix++)
for(iy=0;iy<ny;iy++)
{ i=ny*ix+iy;
 i2=2*i;
 printf("\n %i, %i \t (%lf, \t %lf)",ix,iy,fu2d[i2],fu2d[i2+1]);
}
*/
  /*******************************************************************/
  /************* Allissandrakis solver *******************************/
  /*******************************************************************/
  alpha = 0.0 / (nx - 1); /* specify as start parameter later */
  printf("\n alpha= %lf", alpha);
  fu2d[0] = 0.0;
  fu2d[1] = 0.0; /* Better check flux balance before */

  z = (double *)calloc(nz, sizeof(double));
  kx = (double *)calloc(nxny, sizeof(double)); /* 2D real */
  ky = (double *)calloc(nxny, sizeof(double));
  kz2 = (double *)calloc(nxny, sizeof(double));
  k = (double *)calloc(1 * nxny, sizeof(double));
  iphihat0 = (float *)calloc(2 * nxny, sizeof(float)); /* 2D complex */
  /*
iphihat=(float *) calloc(2*nxny, sizeof(float));
fbx=(float *) calloc(2*nxny, sizeof(float));
fby=(float *) calloc(2*nxny, sizeof(float));
fbz=(float *) calloc(2*nxny, sizeof(float));
*/
  nynz = ny * nz;
  nxnynz = nx * ny * nz;
  Bx = (double *)calloc(nxnynz, sizeof(double));
  By = (double *)calloc(nxnynz, sizeof(double));
  Bz = (double *)calloc(nxnynz, sizeof(double));
  for (iz = 0; iz < nz; iz++)
  {
    z[iz] = 1.0 * iz; /* printf("\n %lf",z[iz]); */
  }

  for (ix = 0; ix < nx; ix++) /* specify kx,ky,kz2, k */
  {
    if (ix <= nx / 2)
    {
      ix2 = ix;
    }
    else
    {
      ix2 = ix - nx;
    }
    for (iy = 0; iy < ny; iy++)
    {
      i = ny * ix + iy;
      kx[i] = 2.0 * PI * ix2 / nx;
      if (iy <= ny / 2)
      {
        iy2 = iy;
      }
      else
      {
        iy2 = iy - ny;
      }
      ky[i] = 2.0 * PI * iy2 / ny;
      kz2[i] = kx[i] * kx[i] + ky[i] * ky[i];
      k[i] = sqrt(kz2[i] - alpha * alpha);
      i2 = 2 * i; /* for complex fields */
      if (ix == 0 && iy == 0)
      {
        iphihat0[i2] = 0.0;
        iphihat0[i2 + 1] = 0.0;
      }
      else
      {
        iphihat0[i2] = fu2d[i2 + 1] / kz2[i]; /* kz2 is real */
        iphihat0[i2 + 1] = -fu2d[i2] / kz2[i];
      }
      /* printf("\n %i, %i \t %lf, \t %lf",ix,iy,iphihat0[i2],iphihat0[i2+1]); */
    }
  }

  /*************Now compute 3D-field upward in z *************************************/
  printf("\n Computing 3D field");

#ifdef _OPENMP
#pragma omp parallel for private(iz, ix, iy, i, i2, i3, iphihat, fbx, fby, fbz)
#endif
  for (iz = 0; iz < nz; iz++)
  { /* printf("\n z= %lf",z[iz]); */
    if (iz % 10 == 0)
    {
      printf("\n Layer z= %i from %i", iz, nz - 1);
    }
    iphihat = (float *)calloc(2 * nxny, sizeof(float));
    fbx = (float *)calloc(2 * nxny, sizeof(float));
    fby = (float *)calloc(2 * nxny, sizeof(float));
    fbz = (float *)calloc(2 * nxny, sizeof(float));
    for (ix = 0; ix < nx; ix++)
    {
      for (iy = 0; iy < ny; iy++)
      {
        i = ny * ix + iy;
        i2 = 2 * i;

        /* This are  2D complex variables,i2 is real, i2+1 imaginary part */
        iphihat[i2] = iphihat0[i2] * exp(-k[i] * z[iz]);
        iphihat[i2 + 1] = iphihat0[i2 + 1] * exp(-k[i] * z[iz]);
        fbx[i2] = (k[i] * kx[i] - alpha * ky[i]) * iphihat[i2];
        fbx[i2 + 1] = (k[i] * kx[i] - alpha * ky[i]) * iphihat[i2 + 1];
        fby[i2] = (k[i] * ky[i] + alpha * kx[i]) * iphihat[i2];
        fby[i2 + 1] = (k[i] * ky[i] + alpha * kx[i]) * iphihat[i2 + 1];
        fbz[i2] = -kz2[i] * iphihat[i2 + 1];
        fbz[i2 + 1] = kz2[i] * iphihat[i2];
        /* printf("\n %i, %i \t %lf, \t %lf",ix,iy,fbz[i2], fbz[i2+1]); */
      }
    }
    DFT2D(fbx, nx, ny, 1);
    DFT2D(fby, nx, ny, 1);
    DFT2D(fbz, nx, ny, 1);

    for (ix = 0; ix < nx; ix++)
    {
      for (iy = 0; iy < ny; iy++)
      {
        i = ny * ix + iy;
        i2 = 2 * i;
        i3 = ix * nynz + iy * nz + iz;
        Bx[i3] = fbx[i2]; /* Only real part! Imaginary part should be 0, but not checked!! */
        By[i3] = fby[i2];
        Bz[i3] = fbz[i2];
      }
    }
    free(iphihat);
    free(fbx);
    free(fby);
    free(fbz);
  }

  time = zeit();
  printf("\n\n Finished! Computing Time = %lf s ", time);
  if (1 == 2)
  {
    if ((initfile = fopen("B02n2.bin", "wb")) == NULL)
    {
      printf("\n Error B02n2.bin");
      exit(1);
    }
    fwrite(Bx, sizeof(double) * nxnynz, 1, initfile);
    fwrite(By, sizeof(double) * nxnynz, 1, initfile);
    fwrite(Bz, sizeof(double) * nxnynz, 1, initfile);
    fclose(initfile);
    printf("\n Big Potential Field written to B02n2.bin \n");
  }
  /*************************************************************************************/
  /*Now cut to original FOV ************************************************************/
  /*************************************************************************************/
  nx2 = nx;
  ny2 = ny;
  nxny2 = nx2 * ny2;
  nynz2 = ny2 * nz;

  if ((initfile = fopen("grid.ini", "r")) == NULL)
  {
    printf("\n Error grid.ini");
    exit(1);
  }
  fscanf(initfile, "%s %i", &leer, &nx);
  fscanf(initfile, "%s %i", &leer, &ny);
  fscanf(initfile, "%s %i", &leer, &nz);
  fclose(initfile);

  nynz = ny * nz;
  nxnynz = nx * ny * nz;
  oBx = (double *)calloc(nxnynz, sizeof(double));
  oBy = (double *)calloc(nxnynz, sizeof(double));
  oBz = (double *)calloc(nxnynz, sizeof(double));

  for (ix = 0; ix < nx; ix++)
    for (iy = 0; iy < ny; iy++)
      for (iz = 0; iz < nz; iz++)
      {
        i = ix * nynz + iy * nz + iz;
        i2 = (ix + xoff) * nynz2 + (iy + yoff) * nz + iz;
        oBx[i] = Bx[i2];
        oBy[i] = By[i2];
        oBz[i] = Bz[i2];
      }

  if ((initfile = fopen("B0.bin", "wb")) == NULL)
  {
    printf("\n Error B0.bin");
    exit(1);
  }
  fwrite(oBx, sizeof(double) * nxnynz, 1, initfile);
  fwrite(oBy, sizeof(double) * nxnynz, 1, initfile);
  fwrite(oBz, sizeof(double) * nxnynz, 1, initfile);
  fclose(initfile);
  printf("\n Potential Field written to B0.bin \n");
}
