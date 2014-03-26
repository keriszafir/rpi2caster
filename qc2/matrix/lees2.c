/* lees 2 */
int reada(int x);

int reada(int x)
{
;
}

int read_mat2( int r,int c, int nr);


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

void nieuw()
{
   char c;
   int i,j,k,l,ii;

   printf("nieuw");

   if (getchar()=='#') exit(1);

   leeg_matrix();/* wis diecase */
		   /* display diecase */

   printf("matrix = leeg ");
   if (getchar()=='#') exit(1);

   disp_matrix();
   if (getchar()=='#') exit(1);

   /* read all places */
   k=0;
   for (j=0;j<14;j++){
      for (i=0;i<16;i++){
	 /* lees matrijs */
	 if (k<MATMAX - 4 ) {
	    for (ii=0;ii<4;ii++) matrix[k].lig[ii]='\0';
	    l = read_mat2(j,i,k);
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
	    } /* einde switch (l) */

	    /* display laatste matrijs * /
	    print_at(24,40,"                    ");
	    print_at(24,40,"aantal records =");
	    printf("%3d ",k+1);
	     */
	    print_at(24,40,"");
	    printf(" r =%2d  c =%2d ",matrix[k].mrij, matrix[k].mkolom);
	    printf(" %d %d ",matrix[k].lig[0],matrix[k].lig[1]);
	    if (getchar()=='#') exit(1);

	    disp_mat( matrix[k] );

	    if (getchar()=='#') exit(1);
	 }
      }
   }
}


int read_mat2 ( int r, int c , int nr )
{
    int l, dikte, i;
    char lees;

    print_at(24,1,"");
    printf(" read_mat2 r = %2d c = %2d nr = %3d ",r,c,nr);
    if (getchar()=='#')exit(1);


    lees = 1;
    matrix[nr].mrij   = r;
    matrix[nr].mkolom = c;
    for (i=0;i<l && i<3  ;i++) matrix[nr].lig[i] = '\0';
    matrix[nr].srt = 0;
    matrix[nr].w = wig[r];


    if ( r ==  0 && c == 8  )
	{ lees = 0; matrix[nr].lig[0]='#'; }
    /*
    if ( r ==  1 && c == 8  )
	{ lees = 0; matrix[nr].lig[0]='#'; }
    if ( r ==  4 && c == 8  )
	{ lees = 0; matrix[nr].lig[0]='#';}
    if ( r == 14 && c == 15 )
	{ lees = 0; matrix[nr].lig[0]='#'; }
    */
    print_at(21,1,"                    ");
    print_at(22,1,"                    ");
    print_at(23,1,"                    ");
    print_at(24,1,"                    hier stoppen ");
    if (getchar()=='#') exit(1);







    return (0);

}

