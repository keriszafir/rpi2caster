/*
   c:\qc2\transltr\gen_syst.c


   23 aug 2004:

      bit setting replaced by adding

   september 2006:

      handling highspaces

*/


float  gegoten_dikte ;
int    i_dik;

unsigned char gn_cc[4];
int    genbufteller ;
int    gen_i, gn_hspi ;
float  gn_delta;
float  gn_epsi ;
int    gn_ccpos;    /* start: actual code for character in buffer */





float gen_system(  unsigned char k, /* kolom */
		   unsigned char r, /* rij   */
		   float dikte      /* width char in units */
		)

{

    gegoten_dikte = 0.;

    i_dik = (int) (dikte * 8. ) ;


    genbufteller = 0;
    gn_hspi=0 ;
    gn_delta = 0. ;
    gn_epsi = 0.0001;
    gn_ccpos=0;    /* start: actual code for character in buffer */
    /* initialize */
    for (gen_i=0; gen_i < 256; gen_i++) cbuff[gen_i] = 0;
    for (gen_i=0; gen_i < 4;   gen_i++) gn_cc[gen_i] = 0;

	/*
       printf("dikte = %7.2f wig %3d  ",dikte,wig[r] );
       printf(" verschil %10.7f ",fabs(dikte - 1.*wig[r]));
       printf(" kleiner %2d ", (fabs(dikte - 1.*wig[r]) < gn_epsi) ? 1 : 0 );
       if ('#'==getchar()) exit(1);
	 */
    if ( dikte ==  wig[r] ) {
      /* i_dik == 8 * wig[r]; */

	/* printf("width equal to wedge \n"); */

	if ( (central.syst == SHIFT) && (r == 15) ) {
	   gn_cc[1] = 0x08;
	} else {
	   for (gen_i=2;gen_i<4;gen_i++) gn_cc[gen_i] = rijcode[r][gen_i];
	}

	       /* for (gen_i=0;gen_i<=3;gen_i++) {
		    printf(" gn_cc[%1d] = %3d ",gen_i,gn_cc[gen_i]);
		    ce();
		  }
		*/
	gegoten_dikte += dikte;

	genbufteller += 4;
	cbuff[4] = 0xff;
    } else {

	if (dikte < wig[r] ) {
	   /* i_dik < 8 * wig[r] */

	   /*
	      printf("width smaller d %6.2f w %3d \n",dikte,wig[r]);
	      getchar();

	    */

	   if ( (r>0) && (dikte == wig[r-1]) && (central.syst == SHIFT ) ) {
			  /* i_dik == 4 * wig[r-1] */

	       /* printf("first branche : using shift \n"); */

	       for (gen_i=2;gen_i<4; gen_i++) {
		  gn_cc[gen_i] = rijcode[r-1][gen_i];
	       }
	       /* i_dik != 8 * wig[r] */

	       gn_cc[1] |= 0x08 ;  /* D */

	       gegoten_dikte += dikte;
	       cbuff[4] |= 0xff;

	   } else {

	       /* printf("second branche \n"); */

	       gn_delta =  dikte - wig[r] ;
	       adjust ( wig[r], gn_delta);

	       /*
		   printf(" correction  u1/u2  %2d / %2d ",
			uitvul[0] ,uitvul[1] ); getchar();
		*/

	       if (central.adding > 0) {  /* unit adding on */

		  /* printf("unit adding on "); getchar();*/

		  cbuff[genbufteller+ 4] = 0x48; /* NK big wedge */
		  cbuff[genbufteller+ 6] = rijcode[uitvul[0] -1][2];
		  cbuff[genbufteller+ 5] = 0x04; /* g = pump on */
		  cbuff[genbufteller+ 7] = rijcode[uitvul[0] -1][3];

		  cbuff[genbufteller+ 8] =  0x44; /* NJ big wedge */
		  cbuff[genbufteller+10] =  rijcode[uitvul[1] -1][2];
		  cbuff[genbufteller+11] =  rijcode[uitvul[1] -1][3];
		  cbuff[genbufteller+11] |= 0x01; /* k = pump off  */
		  cbuff[genbufteller+12] =  0xff;

	       } else {  /* unit adding off */

		  /* printf("unit adding off "); getchar(); */

		  cbuff[genbufteller+ 4] = 0x48; /* NK = pump on */
		  cbuff[genbufteller+ 5] |= 0x04; /* g  */
		  cbuff[genbufteller+ 6] = rijcode[uitvul[0]-1][2];
		  cbuff[genbufteller+ 7] = rijcode[uitvul[0]-1][3];

		  cbuff[genbufteller+ 8] =  0x44; /* NJ = pump off */
		  cbuff[genbufteller+10] =  rijcode[uitvul[1] -1][2];
		  cbuff[genbufteller+11] =  rijcode[uitvul[1] -1][3];
		  cbuff[genbufteller+11] |= 0x01;  /* k  */
		  cbuff[genbufteller+12] =  0xff;
	       }
	       genbufteller += 8;
	       for (gen_i=2; gen_i<4 ; gen_i++) {
		  gn_cc[gen_i] +=  rijcode[r][gen_i];
	       }
	       gn_cc[1] |= 0x20 ; /* S-needle on */
	       gegoten_dikte += dikte;
	   }
	} else {
	   /*

	   print_at(5,1," width is bigger:\n add a high space \n");

	    */
	   gn_hspi = 0;

	   while ( dikte >= (wig[r] + wig[0])) {

	       /* add high space at: O1
		  as long as the desired width is more
		  than wig[0]....

	       */
	       /*
		   i_dik >= 8 * ( wig[r] + wig[0] )

		print_at(6,1," add a high space ");
		if (getchar()=='#') exit(1);
		*/

	       cbuff[genbufteller  ] = 0x80; /* O   */
	       cbuff[genbufteller+2] = 0x40; /* r=1 */
	       genbufteller  += 4; /* raise genbufteller */
		  /*
		       i_dik -= 8 * wig[0] ;
		   */


	       gegoten_dikte += wig[0] ;

	       dikte         -= wig[0] ;

	       gn_ccpos +=4;
	       gn_hspi++;

	   }

	   /*
		at this point the desired width is less than 5 units
		this can be done with the adjustment wedges

	    */

	   if ( (central.adding > 0) && (dikte == (wig[r] + central.adding) )) {

	       /* use unit adding spatieer-wig */
	       gn_cc[1] |= 0x04 ;         /* g = 0x 00 04 00 00 */


	       gegoten_dikte += wig[r] + central.adding ;

	       /*
		  never tested  == dikte ....

		*/

	   } else {  /* aanspatieren */

	       /* printf(" using D10 & D11 wedges \n");*/

	       gn_delta = dikte - wig[r] ;
	       adjust ( wig[r], gn_delta );

	       if (central.adding > 0) {  /* unit adding on */

		  /* printf("unit adding on "); getchar();   */

		  cbuff[genbufteller+ 4]  = 0x48; /* Nk big wedge */
		  cbuff[genbufteller+ 5]  = 0x04; /* g = pump on */
		  cbuff[genbufteller+ 6]  = rijcode[uitvul[0]-1][2];
		  cbuff[genbufteller+ 7]  = rijcode[uitvul[0]-1][3];

		  cbuff[genbufteller+ 8]  = 0x44; /* NJ big wedge */
		  cbuff[genbufteller+10]  = rijcode[uitvul[1] -1][2];
		  cbuff[genbufteller+11]  = rijcode[uitvul[1] -1][3];
		  cbuff[genbufteller+11] |= 0x01; /*   k = pump off */
		  cbuff[genbufteller+12]  = 0xff;

	       } else {  /* printf("unit adding off "); getchar(); */

		  cbuff[genbufteller+ 4]  = 0x48;      /* NK */
		  cbuff[genbufteller+ 5]  = 0x04;      /* g  pump on */
		  cbuff[genbufteller+ 6]  = rijcode[uitvul[0]-1][2];
		  cbuff[genbufteller+ 7]  = rijcode[uitvul[0]-1][3];

		  cbuff[genbufteller+ 8]  = 0x44;      /* NJ */
		  cbuff[genbufteller+10]  = rijcode[uitvul[1] -1][2];
		  cbuff[genbufteller+11]  = rijcode[uitvul[1] -1][3];
		  cbuff[genbufteller+11] |= 0x01;      /* k  pump off */
		  cbuff[genbufteller+12]  = 0xff;
	       }
	       genbufteller += 8;
	       for (gen_i=2;gen_i<4; gen_i++)
		  gn_cc[gen_i] = rijcode[r][gen_i];
	       gn_cc[1] |= 0x20 ;    /* S on */

	       gegoten_dikte += dikte;  /*  += okt 2006 */
	   }
	}
    }

    /* make column code */
    if ( (central.syst == SHIFT) && ( k == 5 ) ) {

	  gn_cc[1] =  0x50; /* EF = D */
    } else {
	  /* 17*15 & 17*16 */
       for (gen_i=0; gen_i<=2; gen_i++)
	  gn_cc[gen_i] |= kolcode[k][gen_i];

       if ( r == 15) {
	  switch (central.syst ) {
	     case MNH :
		switch (k) {
		   case  0 : gn_cc[0] |= 0x01; break; /* H   */
		   case  1 : gn_cc[0] |= 0x01; break; /* H   */
		   case  9 : gn_cc[0] |= 0x40; break; /* N   */
		   case 15 : gn_cc[0] |= 0x20; break; /* M   */
		   case 16 : gn_cc[0]  = 0x61; break; /* HMN */
		   default :
		      gn_cc[0] |= 0x21; break; /* NM  */
		}
		break;
	     case MNK :
		   /*
		byte 1:      byte 2:     byte 3:     byte 4:
		ONML KJIH    GFSE DgCB   A123 4567   89ab cdek
		   */
		switch (k) {
		   case  0 : gn_cc[0] |= 0x08; break; /* NI+K  */
		   case  1 : gn_cc[0] |= 0x08; break; /* NL+K  */
		   case 12 : gn_cc[0] |= 0x40; break; /* N + K */
		   case 14 : gn_cc[0] |= 0x28; break; /* K + M */
		   case 15 : gn_cc[0] |= 0x20; break; /* N + M */
		   case 16 : gn_cc[0]  = 0x68; break; /* NMK   */
		   default : gn_cc[0] |= 0x28; break; /* MK  */
		}
	     break;
	  }
       }
    }

    if ((uitvul[0] == 3) && (uitvul[1]  == 8)) {

	  gn_cc[1] &=  ~0x20; /* mask bit 10 to zero */
	  cbuff[gn_ccpos + 4] = 0xff;
    }
	/* printf(" gn_ccpos = %3d ",gn_ccpos); */

    for (gen_i=0;gen_i<=3;gen_i++) {
       cbuff[gn_ccpos+gen_i] = gn_cc[gen_i]; /* fill buffer  */

		/*   printf(" gn_ccpos+gen_i %3d gn_cc[%1d] = %4d ",gn_ccpos+gen_i,gen_i,gn_cc[gen_i]);
		ce();
		*/
    }

    cbuff[gn_ccpos + genbufteller + 4 - gn_hspi*4 ] = 0xff;

    /*
    printf(" total = %4d ", gn_ccpos + genbufteller + 4 - gn_hspi*4 );
    ce();
       */

    gegoten_dikte *= ( (float) central.set ) /5184. ;

    return(gegoten_dikte);


}   /* end gen_system  */


