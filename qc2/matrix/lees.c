void lees_series()
{
   do {
      cls();
      printf("Series number Monotype ");
      /*      123456890123457891234567890naam2.series = get__int( ); */
      /* int get__int(int r, int cl) */
      naam2.series = get__int( 1, 28 );
   }
      while (naam2.series > 0 );

}




void lees_corps()
{
   naam2.corps = 0;
   do {
      cls();
      print_at(4,5,"Which corps-size             ");
	   /*    1234578901234678901234567890 */
      naam2.corps= get__int(4,25);
   }
      while ( naam2.corps < 6 || naam2.corps> 14 );
   ;
   naam2.corps = 24;
}

void wis_mat(int r, int c)
{
    int wi, wj;
    /* zoek alle records die adres r,c hebben */
    for (wi=0; wi < MATMAX; wi++){
	if (matrix[wi].mrij == r && matrix[wi].mkolom == c ){
	    for (wj=0;wj<4;wj++)
	       matrix[wi].lig[wj]='\0';
	    matrix[wi].mrij   = -1;
	    matrix[wi].mkolom = -1;
	    matrix[wi].w=0;
	    matrix[wi].srt = 0;
	}
    }
}



void lees_set()
{
    double fl;
    int ifl;

    cls();
    print_at(4,5,"Read the set of the diecase ");
    print_at(6,5,"The set = ");
	/*   1234567890123456   */
    do {
	fl = get__float( 6 , 16 );
    }
       while (fl < 5 || fl > 15 );

    fl *= 4.;
    fl += .25;
    ifl =  ( int ) fl;
    fl  =  ( float) ifl;
    fl  /= 4.;

    fset = fl;
    set  = ifl;

    naam2.set = ifl;

}


void copy_mat(int k, int n)
{
    matrix[k+n].lig[0]= matrix[k].lig[0];
    matrix[k+n].lig[1]= matrix[k].lig[1];
    matrix[k+n].lig[2]= matrix[k].lig[2];
    matrix[k+n].lig[3]= matrix[k].lig[3];
    matrix[k+n].w     = matrix[k].w;
    matrix[k+n].mrij  = matrix[k].mrij;
    matrix[k+n].mkolom= matrix[k].mkolom;
}

void lees_wig()
{
    int i,  v = 3, w;

    cls();
    print_at(3,5,"Reading the unit-values of the wedge used ");

    for (i=0; i<15; i++) wig[i] = v;

    for (i=0; i<15; i++){
	do {
	   print_at(6+i,5,     "value of row ");
	   printf("%2d = ",i+1);
	   w = get__dikte(6+i,24);
	}
	   while ( w < v || w > 18 );
	wig[i] = w;
	v = w;
	naam2.wedge[i] = w;
    }
}



void nieuw()
{
   char c;
   int i,j,k,l,ii;

   /*do {
    */
     leeg_matrix();/* wis diecase */
		   /* display diecase */
     disp_matrix();


     /* read all places */
     k=0;
     for (j=0;j<14;j++){
	for (i=0;i<16;i++){
	    /* lees matrijs */
	  if (k<MATMAX - 4 ) {
	    for (ii=0;ii<4;ii++) matrix[k].lig[ii]='\0';

	    l = read_mat(j,i,k);

	    switch ( l ) {
	       case 0 :
		  matrix[k].mrij = j;
		  matrix[k].mkolom = i;
		  matrix[k+1].srt = 0;
		  matrix[k+2].w = 0;
		  break;
	       case 1 :
		  switch ( matrix[k].lig[0] ) {
		     case '.' :
			if (matrix[k].srt == 0 ) {
			   copy_mat(k,1);
			   copy_mat(k,2);
			   matrix[k].srt   = 2;
			   matrix[k+1].srt = 1;
			   matrix[k+2].srt = 0;
			   k+= 2;
			}
			break;
		     case ',' :
			if (matrix[k].srt == 0 ) {
			   copy_mat(k,1);
			   matrix[k].srt   = 2;
			   matrix[k+1].srt = 0;
			   k++;
			}
			break;
		     case '"' :
			if (matrix[k].srt == 0 ) {
			   copy_mat(k,1);
			   matrix[k].srt   = 2;
			   matrix[k+1].srt = 0;
			   k++;
			}
			break;
		     case '\256' :  /* <<  */
			if (matrix[k].srt == 0 ) {
			   copy_mat(k,1);
			   copy_mat(k,2);
			   matrix[k].srt   = 2;
			   matrix[k+1].srt = 1;
			   matrix[k+2].srt = 0;
			   k+=2;
			}
			break;
		     case '\257' :  /* >>  */
			if (matrix[k].srt == 0 ) {
			    copy_mat(k,1);
			    copy_mat(k,2);
			    matrix[k].srt   = 2;
			    matrix[k+1].srt = 1;
			    matrix[k+2].srt = 0;
			     k+=2;
			}
			break;
		      case '!' :
			if (matrix[k].srt == 0 ) {
			   copy_mat(k,1);
			   matrix[k].srt   = 2;
			   matrix[k+1].srt = 0;
			   k++;
			}
			break;
		      case '?' :
			if (matrix[k].srt == 0 ) {
			    copy_mat(k,1);
			    matrix[k].srt   = 2;
			    matrix[k+1].srt = 0;
			    k++;
			}
			break;
		      case '`' :
			if (matrix[k].srt == 0 ) {
			   copy_mat(k,1);
			   matrix[k].srt   = 2;
			   matrix[k+1].srt = 0;
			   k++;
			}
			break;
		      case '-' :
			if (matrix[k].srt == 0 ) {
			   copy_mat(k,1);
			   copy_mat(k,2);
			   matrix[k].srt   = 2;
			   matrix[k+1].srt = 1;
			   matrix[k+2].srt = 0;
			   k+= 2;
			}
			break;
		      case '\'':
			if (matrix[k].srt == 0 ) {
			   copy_mat(k,1);
			   matrix[k].srt   = 2;
			   matrix[k+1].srt = 0;
			   k++;
			}
			break;
		  }
		  break;
	       case 2 :
		   /* -- */
		  if (matrix[k].lig[0] =='-' &&
			 matrix[k].lig[1]=='-' ) {
		      if (matrix[k].srt == 0 ) {
			 copy_mat(k,1);
			 copy_mat(k,2);
			 matrix[k].srt   = 2;
			 matrix[k+1].srt = 1;
			 matrix[k+2].srt = 0;
			 k+= 2;
		      }
		  }
		  break;
	       case 3 :
		  /* --- */
		  if (matrix[k].lig[0] =='-' &&
			 matrix[k].lig[1]=='-' &&
			    matrix[k].lig[2]=='-') {
		     if (matrix[k].srt == 0 ) {
			 copy_mat(k,1);
			 copy_mat(k,2);
			 matrix[k].srt   = 2;
			 matrix[k+1].srt = 1;
			 matrix[k+2].srt = 0;
			 k+= 2;
		     }
		  }
		  if (matrix[k].lig[0] =='.' &&
			 matrix[k].lig[1]=='.' &&
			    matrix[k].lig[2]=='.') {
		     if (matrix[k].srt == 0 ) {
			 copy_mat(k,1);
			 matrix[k].srt   = 2;
			 matrix[k+1].srt = 0;
			 k++;
		     }
		  }
		  break;
	    }

	    print_at(24,40,"                    ");
	    print_at(24,40,"aantal records =");
	    printf("%3d ",k+1);
	      /*
	    print_at(24,40,"");
	    printf(" r =%2d  c =%2d ",matrix[k].mrij, matrix[k].mkolom);
	    printf(" %d %d ",matrix[k].lig[0],matrix[k].lig[1]);
	    if (getchar()=='#') exit(1);
	       */

	    disp_mat( matrix[k] );

	    if (getchar()=='#') exit(1);
	  }
	}
     }
   /*
   }
     while (c !='#');
    */
}




int  read_mat(int r, int c, int nr)
{

    int l, dikte, i;
    char lees;


    lees = 1;
    matrix[nr].mrij   = r;
    matrix[nr].mkolom = c;
    for (i=0;i<l && i<3  ;i++) matrix[nr].lig[i] = '\0';
    matrix[nr].srt = 0;
    matrix[nr].w = wig[r];

    /* high space */
    if ( r ==  0 && c == 8  )
	{ lees = 0; matrix[nr].lig[0]='#'; }
    if ( r ==  1 && c == 8  )
	{ lees = 0; matrix[nr].lig[0]='#'; }
    if ( r ==  4 && c == 8  )
	{ lees = 0; matrix[nr].lig[0]='#';}
    if ( r == 14 && c == 15 )
	{ lees = 0; matrix[nr].lig[0]='#'; }

    print_at(21,1,"                    ");
    print_at(22,1,"                    ");
    print_at(23,1,"                    ");
    print_at(24,1,"                    hier stoppen ");
    if (getchar()=='#') exit(1);


    if ( lees != 0 )
    {
       print_at(21,1,"matrix at : ");
       switch (c)
       {
	  case  0 : printf("NI"); break;
	  case  1 : printf("NL"); break;
	  case  2 : printf("A"); break;
	  case  3 : printf("B"); break;
	  case  4 : printf("C"); break;
	  case  5 : printf("D"); break;
	  case  6 : printf("E"); break;
	  case  7 : printf("F"); break;
	  case  8 : printf("G"); break;
	  case  9 : printf("H"); break;
	  case 10 : printf("I"); break;
	  case 11 : printf("J"); break;
	  case 12 : printf("K"); break;
	  case 13 : printf("L"); break;
	  case 14 : printf("M"); break;
	  case 15 : printf("N"); break;
	  case 16 : printf("O"); break;
       }
       printf("%d",r+1);
       print_at(22,1,"ligature = ");

       l = get_line_at(22,14,3);
       print_at(22,30,"gelezen ");
       for (i=0;i<l;i++) printf("%1c",line_buffer[i] );
       if (getchar()=='#') exit(1);

       matrix[nr].mrij   = r;
       matrix[nr].mkolom = c;
       for (i=0;i<l && i<3  ;i++)
	  matrix[nr].lig[i] = line_buffer[i];

       if ( l == 0 )
       {
	  matrix[nr].w = wig[r];
	  matrix[nr].srt = 0;
       }
       else
       {
	  print_at(23,1,"kind     = ");
	  matrix[nr].srt = get__kind(23,14);
	  do
	  {
	     print_at(24,1,"width    = ");
	     dikte = get__dikte(24,14);
	  }
	     while (dikte<5 ||dikte > 23 );
	  matrix[nr].w = dikte;
	  switch ( l )
	  {
	     case 3 :
		switch (matrix[nr].lig[0])
		{
		   case 'a' :
		      if ( matrix[nr].lig[1]=='e' &&
			  matrix[nr].lig[2]=='!')
		      {
			 matrix[nr].lig[0]=0x91;
			 matrix[nr].lig[1]='\0';
			 matrix[nr].lig[2]='\0';
			 l=1;
		      }
		      break;
		   case 'A' :
		      if ( matrix[nr].lig[1]=='E' &&
			  matrix[nr].lig[2]=='!')
		      {
			 matrix[nr].lig[0]=0x92;
			 matrix[nr].lig[1]='\0';
			 matrix[nr].lig[2]='\0';
			 l=1;
		      }
		      break;
		}
		break;
	     case 2 :
		switch (matrix[nr].lig[0] )
		{
		   case '<':
		      if ( matrix[nr].lig[1] == '<' )
		      {
			 matrix[nr].lig[0] = 0xae;
			 matrix[nr].lig[1] = '\0';
			 l=1;
		      }
		      break;
		   case '>':
		      if ( matrix[nr].lig[1] == '>' )
		      {
			 matrix[nr].lig[0] = 0xaf;
			 matrix[nr].lig[1] = '\0';
			 l=1;
		      }
		      break;
		   default :
		      switch ( matrix[nr].lig[1])
		      {
			 case '^' :
			    switch (matrix[nr].lig[0] )
			    {
			       case 'a' :
				  matrix[nr].lig[0]= 0x83;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'e' :
				  matrix[nr].lig[0]= 0x88;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'i' :
				  matrix[nr].lig[0]= 0x9c;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'o' :
				  matrix[nr].lig[0]= 0x93;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'u' :
				  matrix[nr].lig[0]= 0x96;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'A' :
				  matrix[nr].lig[0]= 0xb6;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'E' :
				  matrix[nr].lig[0]= 0xd2;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'I' :
				  matrix[nr].lig[0]= 0xd7;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'O' :
				  matrix[nr].lig[0]= 0xe2;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'U' :
				  matrix[nr].lig[0]= 0xea;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			    }
			    break;
			 case '"' :
			    switch (matrix[nr].lig[0] )
			    {
			       case 'a' :
				  matrix[nr].lig[0]= 0x84;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'e' :
				  matrix[nr].lig[0]= 0x89;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'i' :
				  matrix[nr].lig[0]= 0x9b;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'o' :
				  matrix[nr].lig[0]= 0x94;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'u' :
				  matrix[nr].lig[0]= 0x81;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'A' :
				  matrix[nr].lig[0]= 0x8e;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'E' :
				  matrix[nr].lig[0]= 0xd3;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'I' :
				  matrix[nr].lig[0]= 0xd8;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'O' :
				  matrix[nr].lig[0]= 0x99;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'U' :
				  matrix[nr].lig[0]= 0x9a;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			    }
			    break;
			 case '`' :
			    switch (matrix[nr].lig[0] )
			    {
			       case 'a' :
				  matrix[nr].lig[0]= 0x85;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'e' :
				  matrix[nr].lig[0]= 0x8a;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'i' :
				  matrix[nr].lig[0]= 0x9d;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'o' :
				  matrix[nr].lig[0]= 0x95;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'u' :
				  matrix[nr].lig[0]= 0x97;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'A' :
				  matrix[nr].lig[0]= 0xb7;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'E' :
				  matrix[nr].lig[0]= 0xd4;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'I' :
				  matrix[nr].lig[0]= 0xde;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'O' :
				  matrix[nr].lig[0]= 0xe3;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'U' :
				  matrix[nr].lig[0]= 0xeb;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			    }
			    break;
			 case '\'':
			    switch (matrix[nr].lig[0] )
			    {
			       case 'a' :
				  matrix[nr].lig[0]= 0xa0;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'e' :
				  matrix[nr].lig[0]= 0x82;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'i' :
				  matrix[nr].lig[0]= 0xa1;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'o' :
				  matrix[nr].lig[0]= 0xa2;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'u' :
				  matrix[nr].lig[0]= 0xa3;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'A' :
				  matrix[nr].lig[0]= 0xb5;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'E' :
				  matrix[nr].lig[0]= 0x90;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'I' :
				  matrix[nr].lig[0]= 0xd6;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'O' :
				  matrix[nr].lig[0]= 0xe0;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'U' :
				  matrix[nr].lig[0]= 0xe9;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			    }
			    break;
			 case '~' :
			    switch (matrix[nr].lig[0] )
			    {
			       case 'n' :
				  matrix[nr].lig[0]= 0xa4;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			       case 'N' :
				  matrix[nr].lig[0]= 0xa5;
				  matrix[nr].lig[1]= '\0';
				  l=1;
				  break;
			    }
			    break;
		      }
		}
		break;
	  }
       }
    }

    return ( l );
}






