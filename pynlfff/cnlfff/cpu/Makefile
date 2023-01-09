
# # Non-parallel
# LDFLAGS = -lm
# CFLAGS = -g -O5
# CC = cc
# RUNDIR = compiled.nonparallel

# parallel
LDFLAGS = -lm -fopenmp
CFLAGS = -g -O5 -fopenmp
CC=gcc # Sometimes adding spaces on both sides of the equal sign may cause compilation errors
RUNDIR = compiled.parallel

# -----------------------------

# # x86 parallel
# LDFLAGS = -lm -m64 -fopenmp
# CFLAGS = -m64 -g -O5 -fopenmp
# CC = cc
# RUNDIR = compiled.parallel

# # for GCC
# LDFLAGS = -lm -m64
# CFLAGS = -m64 -O3 -mtune=native -ffast-math -ftree-vectorize
# CC = gcc
# RUNDIR = compiled.nonparallel

################################

LD = $(CC)
TOOLS = rebin prepro checkquality checkenergy saveboundary fftpot4

all: relax4 $(TOOLS)

RELAX4_SRC = relax1.c \
		init.c \
		loop.c \
		bfield.c \
		optimization.c
RELAX4_OBJ = $(RELAX4_SRC:.c=.o)

relax4:		$(RELAX4_OBJ)
	$(LD) -o $@ $(RELAX4_OBJ) $(LDFLAGS)

$(RELAX4_OBJ):	globals.h  Makefile


## tools
rebin:		rebin3d.o Makefile
	$(LD) -o $@ rebin3d.o $(LDFLAGS)

prepro:		prepro.o Makefile
	$(LD) -o $@ prepro.o $(LDFLAGS)

checkquality:	checkquality.o Makefile
	$(LD) -o $@ checkquality.o $(LDFLAGS)

saveboundary:	saveboundary.o Makefile
	$(LD) -o $@ saveboundary.o $(LDFLAGS)

fftpot4:	fftpot4.o Makefile
	$(LD) -o $@ fftpot4.o $(LDFLAGS)

checkenergy:	checkenergy.o Makefile
	$(LD) -o $@ checkenergy.o $(LDFLAGS)


%.o: %.c
	$(CC) -c $(CFLAGS) $< -o $@

.PHONY: clean 
clean:
	rm -f relax4
	rm -f rebin3d.o
	rm -rf *.o
	rm -f $(RELAX4_OBJ) 
	rm -f $(TOOLS) $(TOOLS:=.o)


install: relax4 $(TOOLS)
	test -d $(RUNDIR) || mkdir $(RUNDIR)
	cp relax4 $(RUNDIR)
	cp $(TOOLS) $(RUNDIR)
	cp multigrid.sh $(RUNDIR)
	chmod +x $(RUNDIR)/*

