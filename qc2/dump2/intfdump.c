void noodstop()
{
   /* printf(" separator = %3x \n", mono.separator); */

   /* mcx[0]=0x44; */ /* NJ */

   printf("Emergency Stop ...........\n");
   printf("The metal-pump is switched off. \n\n");
   printf("The program must be restarted. \n");

   mcx[0]=0x0;
   mcx[1]=0x20; /* S */
   mcx[2]=0x0;
   mcx[3]=0x01; /* 0005 */
   f1();
   zenden_codes();
   zenden_codes();
   init_aan();
   init_uit();





   printf("Emergency Stop ...........\n");
   printf("The metal-pump is switched off. \n\n");
   printf("The program must be restarted. \n");

   if (getchar()=='#') exit(1);

   printf("The button on the interface should be pressed.");

   getchar();

   exit(1);
}


int test_row()
{
    int tt=15;

    if (mono.code[3] & 0x02) tt=14;
    if (mono.code[3] & 0x04) tt=13;
    if (mono.code[3] & 0x08) tt=12;
    if (mono.code[3] & 0x10) tt=11;
    if (mono.code[3] & 0x20) tt=10;
    if (mono.code[3] & 0x40) tt= 9;
    if (mono.code[3] & 0x80) tt= 8;
    if (mono.code[2] & 0x01) tt= 7;
    if (mono.code[2] & 0x02) tt= 6;
    if (mono.code[2] & 0x04) tt= 5;
    if (mono.code[2] & 0x08) tt= 4;
    if (mono.code[2] & 0x10) tt= 3;
    if (mono.code[2] & 0x20) tt= 2;
    if (mono.code[2] & 0x40) tt= 1;

    return(tt);
}

int test_NK()
{
    int t;
    t = mono.code[0] & 0x48;
    return ( t == 0x48 );
}


int test_NJ()
{
    int t;

    t = mono.code[0] & 0x44;
    return( t == 0x44 );
}

int test2_NK()
{
    int t;
    t = mcx[2] & 0x04;
    return ( t == 0x04 );
}

int test2_NJ()
{
    int t;

    t = mcx[3] & 0x01;
    return( t == 0x01 );
}



int test_GS()
{
    int t;

    t = mono.code[1] & 0xa0;
    return ( t == 0xa0);
}

int test_N()
{
    char t;

    t = mono.code[0] & 0x40;
    return( t == 0x40 );
}

int test_k()
{
    char t;

    t = mono.code[3] & 0x01;
    return( t == 0x01 );
}

int test_g()
{
    char t;

    t = mono.code[1] & 0x04;
    return( t == 0x04 );
}

int test_O15()
{
    char t;

    t = 0;
    t += mcx[0]; t += mcx[1];
    t += mcx[2]; t += mcx[3];

    return ( t == 0 );
}


void gotoXY(int row, int column)
{
    _settextposition( row , column );
}


void delay2( int tijd )
{
    long begin_tick, end_tick;
    long i;

    _bios_timeofday( _TIME_GETCLOCK, &begin_tick);
    /* printf(" begin   = %lu \n",begin_tick);*/
    do {

       if (kbhit() ) exit(1);
       _bios_timeofday( _TIME_GETCLOCK, &end_tick);
    }
       while (end_tick < begin_tick + tijd);

    /* printf(" eind    = %lu \n",end_tick); */
    /* printf(" delta   = %lu \n",end_tick- begin_tick); */

    /* while ( end_tick = tijd + begin_tick ) ; */
}

/* control
           sets bit 0, when less than 2 bits are set in mcx[];

*/

void control()
{
    int c = 0;

    if (mcx[0] & 0x40 ) c++;
    if (mcx[0] & 0x20 ) c++;
    if (mcx[0] & 0x10 ) c++;
    if (mcx[0] & 0x08 ) c++;
    if (mcx[0] & 0x04 ) c++;
    if (mcx[0] & 0x02 ) c++;
    if (mcx[0] & 0x01 ) c++;

    if (mcx[1] & 0x80 ) c++;
    if (mcx[1] & 0x40 ) c++;
    if (mcx[1] & 0x20 ) c++;
    if (mcx[1] & 0x10 ) c++;
    if (mcx[1] & 0x08 ) c++;
    if (mcx[1] & 0x04 ) c++;
    if (mcx[1] & 0x02 ) c++;
    if (mcx[1] & 0x01 ) c++;

    if (mcx[2] & 0x80 ) c++;
    if (mcx[2] & 0x40 ) c++;
    if (mcx[2] & 0x20 ) c++;
    if (mcx[2] & 0x10 ) c++;
    if (mcx[2] & 0x08 ) c++;
    if (mcx[2] & 0x04 ) c++;
    if (mcx[2] & 0x02 ) c++;
    if (mcx[2] & 0x01 ) c++;

    if (mcx[3] & 0x80 ) c++;
    if (mcx[3] & 0x40 ) c++;
    if (mcx[3] & 0x20 ) c++;
    if (mcx[3] & 0x10 ) c++;
    if (mcx[3] & 0x08 ) c++;
    if (mcx[3] & 0x04 ) c++;
    if (mcx[3] & 0x02 ) c++;
    if (mcx[3] & 0x01 ) c++;

    if ( caster == 'k' ) {
	 /* mcx[0] &= 0x7f; delete first bit by caster */

	 if ( c < 2 ) mcx[0] |= 0x80; /* put highest bit on  */
    }

}




void dispmono()
{

    gotoXY(22,8);


    if (mono.code[0] & 0x80 ) printf("O");
    if (mono.code[0] & 0x40 ) printf("N");
    if (mono.code[0] & 0x20 ) printf("M");
    if (mono.code[0] & 0x10 ) printf("L");
    if (mono.code[0] & 0x08 ) printf("K");
    if (mono.code[0] & 0x04 ) printf("J");
    if (mono.code[0] & 0x02 ) printf("I");
    if (mono.code[0] & 0x01 ) printf("H");
    if (mono.code[1] & 0x80 ) printf("G");
    if (mono.code[1] & 0x40 ) printf("F");
    if (mono.code[1] & 0x20 ) printf("s");
    if (mono.code[1] & 0x10 ) printf("E");
    if (mono.code[1] & 0x08 ) printf("D");
    if (mono.code[1] & 0x04 ) printf("-0075-");
    if (mono.code[1] & 0x02 ) printf("C");
    if (mono.code[1] & 0x01 ) printf("B");
    if (mono.code[2] & 0x80 ) printf("A");
    printf("-");
    if (mono.code[2] & 0x40 ) printf("1");
    if (mono.code[2] & 0x20 ) printf("2");
    if (mono.code[2] & 0x10 ) printf("3");
    if (mono.code[2] & 0x08 ) printf("4");
    if (mono.code[2] & 0x04 ) printf("5");
    if (mono.code[2] & 0x02 ) printf("6");
    if (mono.code[2] & 0x01 ) printf("7");
    if (mono.code[3] & 0x80 ) printf("8");
    if (mono.code[3] & 0x40 ) printf("9");
    if (mono.code[3] & 0x20 ) printf("10");
    if (mono.code[3] & 0x10 ) printf("11");
    if (mono.code[3] & 0x08 ) printf("12");
    if (mono.code[3] & 0x04 ) printf("13");
    if (mono.code[3] & 0x02 ) printf("14");
    if (mono.code[3] & 0x01 ) printf("-0005");
    printf("               ");

    /* zenden() */
}



void di_spcode()
{

    gotoXY(22,8);

    /*
    printf("%2x ",mcx[0]); printf("%2x ",mcx[1]);
    printf("%2x ",mcx[2]); printf("%2x ",mcx[3]);
     */

    if (mcx[0] & 0x80 ) printf("O");
    if (mcx[0] & 0x40 ) printf("N");
    if (mcx[0] & 0x20 ) printf("M");
    if (mcx[0] & 0x10 ) printf("L");
    if (mcx[0] & 0x08 ) printf("K");
    if (mcx[0] & 0x04 ) printf("J");
    if (mcx[0] & 0x02 ) printf("I");
    if (mcx[0] & 0x01 ) printf("H");
    if (mcx[1] & 0x80 ) printf("G");
    if (mcx[1] & 0x40 ) printf("F");
    if (mcx[1] & 0x20 ) printf("s");
    if (mcx[1] & 0x10 ) printf("E");
    if (mcx[1] & 0x08 ) printf("D");
    if (mcx[1] & 0x04 ) printf("-w75-");
    if (mcx[1] & 0x02 ) printf("C");
    if (mcx[1] & 0x01 ) printf("B");
    if (mcx[2] & 0x80 ) printf("A");
    printf("-");
    if (mcx[2] & 0x40 ) printf("1");
    if (mcx[2] & 0x20 ) printf("2");
    if (mcx[2] & 0x10 ) printf("3");
    if (mcx[2] & 0x08 ) printf("4");
    if (mcx[2] & 0x04 ) printf("5");
    if (mcx[2] & 0x02 ) printf("6");
    if (mcx[2] & 0x01 ) printf("7");
    if (mcx[3] & 0x80 ) printf("8");
    if (mcx[3] & 0x40 ) printf("9");
    if (mcx[3] & 0x20 ) printf("10");
    if (mcx[3] & 0x10 ) printf("11");
    if (mcx[3] & 0x08 ) printf("12");
    if (mcx[3] & 0x04 ) printf("13");
    if (mcx[3] & 0x02 ) printf("14");
    if (mcx[3] & 0x01 ) printf("-w05");
    printf("               ");

    /* zenden() */
}


/*
    this routine uses quite some basic machine-language 
    for the interaction with the interface

    the bytes are sent
    



 */


void zenden_codes()
{
     int ziii, zjj;

     /*
     if (mcx[3] & 0x01 ) mcx[0] |= 0x44; / * NJ * /

     if (mcx[1] & 0x04 ) mcx[0] |= 0x48; / * NK * /
      */
     /*
     if ( test2_NJ() ) {
	if ( test2_NJ() ) {
	    mcx[0] = 0x4c ;
	} else {
	    mcx[0] = 0x44;
	}
     } else {
	  if (test2_NK () )
	    mcx[0] = 0x48;
     }


     ontcijfer();

     */


     if ( test_k() ) { /* voor even nu */
         mcx[1] |= 0x20;
     }


     if (test_g() ) {
	  mcx[1] |= 0x20;
	  /* mcx[1] &= 0x20; */
     }



     if (mcx[0] & 0x40 ) mcx[0] |= 0x80;

	  control();

	  busy_uit();  /* sent no data while busy == on */
	  outp(poort , mcx[0]  );
	  /* byte 0 out : when busy == on, you can't give a strobe  */
	  busy_uit();     /* data stable ? + safety-check */
	  outp( poort + 2, inp(poort+2) | 0x01);  /* STROBE ON */
	  busy_aan();              /* has interface seen data */
				   /* data received */
	  outp( poort + 2, inp(poort+2) &~ 0x01); /* STROBE OUT */
	  busy_uit();  /* wait until data is processed by interface */

	  outp(poort , mcx[1]  );  /*  byte 1 data out */
	  busy_uit();
	  outp( poort + 2, inp(poort+2) | 0x01);  /* STROBE ON */
	  busy_aan();              /* has interface seen data */
				   /* data received */
	  outp( poort + 2, inp(poort+2) &~ 0x01); /* STROBE OUT */
	  busy_uit();   /* wait until data is processed  */


	  outp(poort , mcx[2] );   /*  byte 2 data out */
	  busy_uit();
	  outp( poort + 2, inp(poort+2) | 0x01);  /* STROBE ON */
	  busy_aan();              /* has interface seen data */
				   /* data received */
	  outp( poort + 2, inp(poort+2) &~ 0x01); /* STROBE OUT */
	  busy_uit();   /* wait until data is processed */


	  outp(poort , mcx[3] );   /*  byte 3 data out */
	  busy_uit();
	  outp( poort + 2, inp(poort+2) | 0x01);  /* STROBE ON */
	  busy_aan();              /* has interface seen data */
				   /* data received */
	  outp( poort + 2, inp(poort+2) &~ 0x01); /* STROBE OUT */

	  /* 4 bytes sent: the interface is busy...
		 the program takes over, and prepares the next
		 4 bytes
	   */
	   if ( caster == 'k' ) {
	       busy_uit(); /* wait until the flag is
		              completely down, and the lightswitch has
		                changed status
			        */

	       delay2(8); /* wait until the flag is moved back
		               completely by the machine self ...
			*/
	   }
}


void init_uit()
{
    outp(poort + 2 , inp(poort + 2) | 0x04 );   /* remove init   */
}

void inits_uit()
{

    outp(poort1 + 2 , inp(poort1 + 2) | 0x04 );   /* remove init   */
    outp(poort2 + 2 , inp(poort2 + 2) | 0x04 );   /* remove init   */
    outp(poort3 + 2 , inp(poort3 + 2) | 0x04 );   /* remove init   */
}



void init_aan()
{
    outp(poort + 2 , inp(poort + 2) &~0x04);    /* initialize    */
}


void init()
{
    init_aan();  /*  port+2 &= ~0x04  aanzetten */
    busy_aan();  /* wait until busy changes        */
    init_uit();  /*  port+2 |=  0x04  uitzetten */
    printf(" Waiting until the SET-button is pressed.\n");

    busy_uit();  /*  wait until busy is off  */
}

void strobe_on ()
{
   coms = inp( poort + 2) | 0x01;
   outp( poort + 2, coms ); /* set bit */
}

void strobe_out()
{
   coms = inp (poort + 2) & ~0x01;
   outp( poort + 2, coms ); /* clear bit */
}

void strobes_out()
{
   if ( inp(poort1+2) & 0x01 )
       outp( poort1 + 2, inp(poort1+2) & ~ 0x01); /* clear bit */
   if ( inp(poort2+2) & 0x01 )
       outp( poort2 + 2, inp(poort2+2) & ~ 0x01); /* clear bit */
   if ( inp(poort3+3) & 0x01 )
       outp( poort3 + 2, inp(poort3+2) & ~ 0x01); /* clear bit */
}

char b_c;

void busy_aan()

/* Zolang BUSY nog een 0 is lezen we de status af            */
/* Als de machine 'vaststaat' is er de nooddeur              */
/* Programma staat 90% van de tijd in deze lussen te wachten

       the status-byte is only to be read

       meaning of the bits:

       busy       0x80
       ACK        0x40
       paper out  0x20
       select     0x10
       error      0x08

       on some machines these bits can be inverted


 */

{
     status = 0x00;

     while ( status != 0x80 )
     {
	  status = inp (poort + 3 );   /* hogere registers     */

	  /* this code looks redundant :

	     the result is ignored anyway,

	     still it cannot be avoided, because some Windows/MS-DOS
	     computers will render NO RESULT, when the higher registers
	     are NOT READ, BEFORE the lower registers .

	     some computers do not need it,

	     This cannot be predicted, because the obvious lack of
	     documentation about the changes ( Microsoft ?) made in
	     the protocols.

	   */

	  status = inp (poort + 1 );
	  status = status & 0x80;

	       /*

	       LEES STATUSBYTE : clear all bits, but the highest

	       if this bit is set: the busy is ON...

	       */

	 /*  gotoXY ( 48, 18); printf(" %2x",status); */
	  if ( status == 0x80 ) {
	      if ( kbhit() ) {
		 b_c = getch();
		 if ( b_c==']' ) {
		    printf("Busy uit -> noodstop \n");
		    noodstop();

		 }
	      }
	  }
     }
}



void cls()
{
     _clearscreen(  _GCLEARSCREEN );
}

/* uses: strobes_out() , inits_uit() */

void zoekpoort()
{
     int ntry = 0;

     do {

	statx1 = inp ( poort1 + 3 );
	statx2 = inp ( poort1 + 4 );
	stat1  = inp ( poort1 + 1 );

	statx1 = inp ( poort2 + 3 );
	statx2 = inp ( poort2 + 4 );
	stat2  = inp ( poort2 + 1 );

	statx1 = inp ( poort3 + 3 );
	statx2 = inp ( poort3 + 4 );
	stat3  = inp ( poort3 + 1 );

	if (stat1 == 0xff && stat2 == 0xff && stat3 == 0xff) {
	   printf("Put busy out : ");

	   strobes_out();  /* all strobes off */
	   inits_uit();    /* all inits off   */


	   ntry++;

	   if (ntry > 4 ) {
	      printf("After 4 trials, all ports not available \n");
	      printf("Check your hardware, the program will stop, \n");
	      printf("After a character is entered ");
	      getchar();
	      exit(1);
	   }
	      if (getchar()=='#') exit(1);
	}
     }
     while (stat1 == 0xff && stat2 ==0xff && stat3 == 0xff);


     printf(" Determinating the active port...\n");
     printf("\n");
     vlag =  FALSE;
     while ( ! vlag )
     {
	  pnr = 0;
	  stat1 =  inp( poort1 + 1 );
	  if ( stat1 != 0xFF )
	  {
	       vlag  =  TRUE;
	       poort =  poort1;
	       pnr   =  1;
	       printf(" Found at port 1 address 278 hex\n");
	       getchar();
	  }
	  stat2 =  inp( poort2 + 1);
	  if ( stat2 != 0xFF )
	  {
	       vlag  =  TRUE;
	       poort =  poort2;
	       pnr   =  2;
	       printf(" Found at port 2 address 378 hex\n");
	       getchar();
	  }
	  stat3 =  inp( poort3 + 1);
	  if ( stat3 != 0xFF )
	  {
	       vlag  =  TRUE;
	       poort =  poort3;
	       pnr   =  3;
	       printf(" Found at port 3 address 3BC hex\n");
	       getchar();
	  }
	  if ( ! vlag )
	  {
	       ntry++;
	       printf(" Trial %2d \n",ntry);
	       printf(" I cannot deterine the active port.\n");
	       printf(" Maybe the SET-button is not pressed.\n");
	       printf("\n");

     /* u DIRECT de heer Cornelisse te bellen\n");
     printf("telefoon 0115491184 [geheim nummer, dus houdt het geheim]\n");
     printf("en SUBIET te eisen dat uw apparaat per brommer door hem\n");
     printf("persoonlijk wordt afgehaald.\n");
	       */
	       if (ntry >= 4) {
		   printf(" Unfortunately you must restart the program.\n");
		   printf(" and follow the instructions in time.\n");
		   printf("\n");
		   printf(" If the problems continue, \n");
		   printf(" the interface might be not connected or defect .\n");


		   exit(1);
	       }
	  }

     }
     printf(" Basic address for IO set at ");
     printf("%8d ",poort);
     printf(" = 0x%3x (hex) ",poort );
     printf("\n");


     /*
     printf(" If this is not correct, you can halt the program with <#> \n");
     printf("\n");
     printf(" Hit any key to proceed.");
     while ( ! kbhit() );
      */

}



void busy_uit()

/* Zolang BUSY nog een 1 is lezen we de status af            */
/* Als de machine 'vaststaat' is er de nooddeur              */
/* Programma staat 90% van de tijd in deze lussen te wachten */

{
     status = 0x80;

     while ( status == 0x80 )
     {
	  status = inp ( poort + 3 ); /* reach to higher registers
		 do not anything with it, but without it, you will
		 not get the right informtation f

	  */
	  status = inp ( poort + 1 ); /* read status-byte */
	  status = status & 0x80 ;


     /*   gotoXY ( 10, 18); printf(" %2x",status); */

	  if ( status == 0x80 ) {
	      if ( kbhit() ) {
		 b_c = getch();
		 if ( b_c==']' ) {
		    printf("Busy uit -> noodstop \n");
		    noodstop();
		 }
	      }
	  }
     }
}


void disp_bytes()
{
    int ni;

    for (ni = 0; ni<36; ni++) printf("%1c",ontc[ni]);
    printf("    ");
    for (ni=0; ni<ncode; ni++) {
       if (mcode[ni] != ' ') printf("%c",mcode[ni]);
    }
    printf("\n");
}

void cijfer();

void cijfer()
{
    int ni=0;

    ncode=0;

    if (mono.code[0] & 0x80) { ontc[ 0]='1'; mcode[ncode++]='O'; ni++; };
    if (mono.code[0] & 0x40) { ontc[ 1]='1'; mcode[ncode++]='N'; ni++; };
    if (mono.code[0] & 0x20) { ontc[ 2]='1'; mcode[ncode++]='M'; ni++; };
    if (mono.code[0] & 0x10) { ontc[ 3]='1'; mcode[ncode++]='L'; ni++; };
    if (mono.code[0] & 0x08) { ontc[ 4]='1'; mcode[ncode++]='K'; ni++; };
    if (mono.code[0] & 0x04) { ontc[ 5]='1'; mcode[ncode++]='J'; ni++; };
    if (mono.code[0] & 0x02) { ontc[ 6]='1'; mcode[ncode++]='I'; ni++; };
    if (mono.code[0] & 0x01) { ontc[ 7]='1'; mcode[ncode++]='H'; ni++; };
    ontc[8]=' ';
    if (mono.code[1] & 0x80) { ontc[ 9]='1'; mcode[ncode++]='G'; ni++; };
    if (mono.code[1] & 0x40) { ontc[10]='1'; mcode[ncode++]='F'; ni++; };
    if (mono.code[1] & 0x20) { ontc[11]='1'; mcode[ncode++]='S'; };
    if (mono.code[1] & 0x10) { ontc[12]='1'; mcode[ncode++]='E'; ni++; };
    if (mono.code[1] & 0x08) { ontc[13]='1'; mcode[ncode++]='D'; ni++; };
    if (mono.code[1] & 0x04) { ontc[14]='1'; mcode[ncode++]='g'; };
    if (mono.code[1] & 0x02) { ontc[15]='1'; mcode[ncode++]='C'; ni++; };
    if (mono.code[1] & 0x01) { ontc[16]='1'; mcode[ncode++]='B'; ni++; };
    ontc[17]=' ';
    if (mono.code[2] & 0x80) { ontc[18]='1'; mcode[ncode++]='A'; ni++; };
    if (ni == 0 ) mcode[ncode++] ='O';
    ni  = 0;
    if (mono.code[2] & 0x40) { ontc[19]='1'; mcode[ncode++]='1'; ni++; };
    if (mono.code[2] & 0x20) { ontc[20]='1'; mcode[ncode++]='2'; ni++; };
    if (mono.code[2] & 0x10) { ontc[21]='1'; mcode[ncode++]='3'; ni++; };
    if (mono.code[2] & 0x08) { ontc[22]='1'; mcode[ncode++]='4'; ni++; };
    if (mono.code[2] & 0x04) { ontc[23]='1'; mcode[ncode++]='5'; ni++; };
    if (mono.code[2] & 0x02) { ontc[24]='1'; mcode[ncode++]='6'; ni++; };
    if (mono.code[2] & 0x01) { ontc[25]='1'; mcode[ncode++]='7'; ni++; };
    ontc[26]=' ';
    if (mono.code[3] & 0x80) { ontc[27]='1'; mcode[ncode++]='8'; ni++; };
    if (mono.code[3] & 0x40) { ontc[28]='1'; mcode[ncode++]='9'; ni++; };
    if (mono.code[3] & 0x20) { ontc[29]='1'; mcode[ncode++]='a'; ni++; };
    if (mono.code[3] & 0x10) { ontc[30]='1'; mcode[ncode++]='b'; ni++; };
    if (mono.code[3] & 0x08) { ontc[31]='1'; mcode[ncode++]='c'; ni++; };
    if (mono.code[3] & 0x04) { ontc[32]='1'; mcode[ncode++]='d'; ni++; };
    if (mono.code[3] & 0x02) { ontc[33]='1'; mcode[ncode++]='e'; ni++; };
    if (ni == 0 ) mcode[ncode++] = 'f';
    if (mono.code[3] & 0x01) { ontc[34]='1'; mcode[ncode++]='k'; };
    mcode[ncode]='\0';
    ontc[35]=' ';

}

void ontcijfer()
{
    int ni=0;

    for (ncode=0;ncode<36;ncode++) ontc[ncode]='0';
    ontc[8] = ' ';
    ontc[17] = ' ';

    cijfer();
    /*
    ncode=0;

    if (mono.code[0] & 0x80) { ontc[ 0]='1'; mcode[ncode++]='O'; ni++; };
    if (mono.code[0] & 0x40) { ontc[ 1]='1'; mcode[ncode++]='N'; ni++; };
    if (mono.code[0] & 0x20) { ontc[ 2]='1'; mcode[ncode++]='M'; ni++; };
    if (mono.code[0] & 0x10) { ontc[ 3]='1'; mcode[ncode++]='L'; ni++; };
    if (mono.code[0] & 0x08) { ontc[ 4]='1'; mcode[ncode++]='K'; ni++; };
    if (mono.code[0] & 0x04) { ontc[ 5]='1'; mcode[ncode++]='J'; ni++; };
    if (mono.code[0] & 0x02) { ontc[ 6]='1'; mcode[ncode++]='I'; ni++; };
    if (mono.code[0] & 0x01) { ontc[ 7]='1'; mcode[ncode++]='H'; ni++; };

    if (mono.code[1] & 0x80) { ontc[ 9]='1'; mcode[ncode++]='G'; ni++; };
    if (mono.code[1] & 0x40) { ontc[10]='1'; mcode[ncode++]='F'; ni++; };
    if (mono.code[1] & 0x20) { ontc[11]='1'; mcode[ncode++]='S'; };
    if (mono.code[1] & 0x10) { ontc[12]='1'; mcode[ncode++]='E'; ni++; };
    if (mono.code[1] & 0x08) { ontc[13]='1'; mcode[ncode++]='D'; ni++; };
    if (mono.code[1] & 0x04) { ontc[14]='1'; mcode[ncode++]='g'; };
    if (mono.code[1] & 0x02) { ontc[15]='1'; mcode[ncode++]='C'; ni++; };
    if (mono.code[1] & 0x01) { ontc[16]='1'; mcode[ncode++]='B'; ni++; };

    if (mono.code[2] & 0x80) { ontc[18]='1'; mcode[ncode++]='A'; ni++; };
    if (ni == 0 ) mcode[ncode++] ='O';
    ni  = 0;
    if (mono.code[2] & 0x40) { ontc[19]='1'; mcode[ncode++]='1'; ni++; };
    if (mono.code[2] & 0x20) { ontc[20]='1'; mcode[ncode++]='2'; ni++; };
    if (mono.code[2] & 0x10) { ontc[21]='1'; mcode[ncode++]='3'; ni++; };
    if (mono.code[2] & 0x08) { ontc[22]='1'; mcode[ncode++]='4'; ni++; };
    if (mono.code[2] & 0x04) { ontc[23]='1'; mcode[ncode++]='5'; ni++; };
    if (mono.code[2] & 0x02) { ontc[24]='1'; mcode[ncode++]='6'; ni++; };
    if (mono.code[2] & 0x01) { ontc[25]='1'; mcode[ncode++]='7'; ni++; };
    ontc[26]=' ';
    if (mono.code[3] & 0x80) { ontc[27]='1'; mcode[ncode++]='8'; ni++; };
    if (mono.code[3] & 0x40) { ontc[28]='1'; mcode[ncode++]='9'; ni++; };
    if (mono.code[3] & 0x20) { ontc[29]='1'; mcode[ncode++]='a'; ni++; };
    if (mono.code[3] & 0x10) { ontc[30]='1'; mcode[ncode++]='b'; ni++; };
    if (mono.code[3] & 0x08) { ontc[31]='1'; mcode[ncode++]='c'; ni++; };
    if (mono.code[3] & 0x04) { ontc[32]='1'; mcode[ncode++]='d'; ni++; };
    if (mono.code[3] & 0x02) { ontc[33]='1'; mcode[ncode++]='e'; ni++; };
    if (ni == 0 ) mcode[ncode++] = 'f';
    if (mono.code[3] & 0x01) { ontc[34]='1'; mcode[ncode++]='k'; };
    mcode[ncode]='\0';
    ontc[35]=' ';
    */

    /*
    for ( ni =0; ni<=35; ni++) printf("%1c",ontc[ni]);

    for ( ni=0; ni<ncode; ni++)
	printf("%1c",mcode[ni]);
    printf("\n");
    */
}



void ontcijfer2()
{
    int ni,nj;

    for (ncode=0;ncode<36;ncode++) ontc[ncode]='0';

    for (ni = 0; ni<4 ; ni++) mono.code[ni]=mcx[ni];


    ncode=0;
    mcode[ncode++]=' ';


    printf("Gegoten        %5d : ",  gegoten);
    cijfer();

    /*
    if (mcx[0] & 0x80) { ontc[ 0]='1'; mcode[0]='O';       ni++; };
    if (mcx[0] & 0x40) { ontc[ 1]='1'; mcode[ncode++]='N'; ni++; };
    if (mcx[0] & 0x20) { ontc[ 2]='1'; mcode[ncode++]='M'; ni++; };
    if (mcx[0] & 0x10) { ontc[ 3]='1'; mcode[ncode++]='L'; ni++; };
    if (mcx[0] & 0x08) { ontc[ 4]='1'; mcode[ncode++]='K'; ni++; };
    if (mcx[0] & 0x04) { ontc[ 5]='1'; mcode[ncode++]='J'; ni++; };
    if (mcx[0] & 0x02) { ontc[ 6]='1'; mcode[ncode++]='I'; ni++; };
    if (mcx[0] & 0x01) { ontc[ 7]='1'; mcode[ncode++]='H'; ni++; };
    ontc[8]=' ';
    if (mcx[1] & 0x80) { ontc[ 9]='1'; mcode[ncode++]='G'; ni++; };
    if (mcx[1] & 0x40) { ontc[10]='1'; mcode[ncode++]='F'; ni++; };
    if (mcx[1] & 0x20) { ontc[11]='1'; mcode[ncode++]='S'; };
    if (mcx[1] & 0x10) { ontc[12]='1'; mcode[ncode++]='E'; ni++; };

    if (mcx[1] & 0x08) { ontc[13]='1'; mcode[ncode++]='D'; ni++; };
    if (mcx[1] & 0x04) { ontc[14]='1'; mcode[ncode++]='g'; ni++; };
    if (mcx[1] & 0x02) { ontc[15]='1'; mcode[ncode++]='C'; ni++; };
    if (mcx[1] & 0x01) { ontc[16]='1'; mcode[ncode++]='B'; ni++; };
    ontc[17]=' ';
    if (mcx[2] & 0x80) { ontc[18]='1'; mcode[ncode++]='A'; ni++; };
    if (ni == 0 && ! (mcx[3] & 0x01 )) mcode[0] ='O';
    if (ni == 2 ) {
       if (mcode[1] == 'N') {
	  if ( mcode[2] != 'I' && mcode[2] != 'L'
	       && mcode[2] != 'J'&& mcode[2] != 'K' ) {
	     printf("column-code incorrect.");
	     for (nj=0;nj<ncode;nj++){
		printf("%1c",mcode[nj]);
	     }
	     if (getchar()=='#') exit(1) ;
	  }
       } else {

       }

    }
    ni  = 0;
    if (mcx[2] & 0x40) { ontc[19]='1'; mcode[ncode++]='1'; ni++; };
    if (mcx[2] & 0x20) { ontc[20]='1'; mcode[ncode++]='2'; ni++; };
    if (mcx[2] & 0x10) { ontc[21]='1'; mcode[ncode++]='3'; ni++; };

    if (mcx[2] & 0x08) { ontc[22]='1'; mcode[ncode++]='4'; ni++; };
    if (mcx[2] & 0x04) { ontc[23]='1'; mcode[ncode++]='5'; ni++; };
    if (mcx[2] & 0x02) { ontc[24]='1'; mcode[ncode++]='6'; ni++; };
    if (mcx[2] & 0x01) { ontc[25]='1'; mcode[ncode++]='7'; ni++; };
    ontc[26]=' ';
    if (mcx[3] & 0x80) { ontc[27]='1'; mcode[ncode++]='8'; ni++; };
    if (mcx[3] & 0x40) { ontc[28]='1'; mcode[ncode++]='9'; ni++; };
    if (mcx[3] & 0x20) { ontc[29]='1'; mcode[ncode++]='a'; ni++; };
    if (mcx[3] & 0x10) { ontc[30]='1'; mcode[ncode++]='b'; ni++; };
    if (mcx[3] & 0x08) { ontc[31]='1'; mcode[ncode++]='c'; ni++; };
    if (mcx[3] & 0x04) { ontc[32]='1'; mcode[ncode++]='d'; ni++; };
    if (mcx[3] & 0x02) { ontc[33]='1'; mcode[ncode++]='e'; ni++; };
    if (ni == 0 ) mcode[ncode++]='f';
    if (mcx[3] & 0x01) { ontc[34]='1'; mcode[ncode++]='k'; };
    ontc[35]=' ';
    */

    mcode[ncode]='\0';

    disp_bytes();

    /*
    for (ni = 0; ni<36; ni++) printf("%1c",ontc[ni]);
    printf("     ");
    for (ni=0; ni<ncode; ni++) {
       if (mcode[ni] != ' ') printf("%c",mcode[ni]);
    }
    printf(" l %3d\n",regelnr);
    */

    if ( test_k() ) {
	  p0005 = test_row();
        mcx[1] |= 0x20;
    }
    if ( test_g() ) {
	  p0075 = test_row();
        mcx[1] |= 0x20;
    }
}



void startinterface()
{
    char stpp;



    if ( interf_aan != 1 ) {

       cls();
       printf("\n\n\n\n\ninteraction interface \n\n");
       do {
	  printf("Interface in use ? ");
	  stpp = getchar();
       } while (stpp != 'j' && stpp != 'n' && stpp != 'y'
	     && stpp == 'J' && stpp != 'N' && stpp != 'Y'  );
       switch( stpp){
	  case 'y' : stpp = 'j'; break;
	  case 'Y' : stpp = 'j'; break;
	  case 'J' : stpp = 'j'; break;
	  case 'N' : stpp = 'n'; break;
       }

       if (stpp == 'j' ) {

	  printf(" Before we proceed, if the light is ON at the\n");
	  printf(" SET-button ON, then the SET-button must be pressed.\n");
	  printf("\n");

	  do {
	     printf("Put the reset-button on \n\n");
	     getchar();
	     printf("Keyboard or caster <k/c> ");
	     caster = getchar();
	     printf(" caster == %1c %3d ",caster,caster);

	     if (getchar()=='#') exit(1);
	  }
	     while (caster != 'k' && caster != 'c' && caster != 'e' );

	  if (caster == 'e' ) {
	     interf_aan = 0;

	  } else {

	    printf(" Before we proceed, if the light is ON at the\n");
	    printf(" SET-button ON, then the SET-button must be pressed.\n");
	    printf("\n");
	    printf(" Hit any key, when this is the case...\n");
	    /* ungetch(ch); */

	    if ( getchar()=='#') exit(1);

	    init_uit();
	    strobe_out();
	    zoekpoort();
	    coms =  inp( poort + 2);
	    init();
	    interf_aan = 1;
	  }
       }
       printf("Interface is switched ");
       printf( interf_aan == 0 ? "off\n" : "on\n" );
       if (getchar()=='#') exit(1) ;
    }
}

