/**********************/
/* matrix-c           */
/**********************/

void vulm(char l[], unsigned char k, unsigned char w, unsigned char row,
		   unsigned char col);
unsigned int instal_matrix(void);    /* default matrix        */

void matrix_gereedmaken(void);       /* init matrix pointers */

unsigned int matrix_inlezen(void);   /* read matrix */

void schrijf_matrix();               /* store on disc */

void display_matrix();               /* display on screen */


void vulm(char l[], unsigned char k, unsigned char w, unsigned char row,
		   unsigned char col)
{
    int i;
    char c;

    for (i=0; i<=3 && ((c = l[i])!='\0');i++){
	matrix[row][col]->ligature[i]=l[i];
    }
    matrix[row][col] -> kind = k;
    matrix[row][col] -> width = w;
    matrix[row][col] -> row = row;
    matrix[row][col] -> col = col;
}

unsigned int instal_matrix(void)    /* default matrix */
{
    vulm("j",1,5,0, 0); vulm("l",1,5,0, 1); vulm("i",1,5,0, 2);
    vulm(":",1,5,0, 3); vulm(",",0,5,0, 4); vulm("'",0,5,0, 5);
    vulm("j",0,5,0, 6); vulm("i",0,5,0, 7); vulm(" ",0,5,0, 8);
    vulm("l",0,5,0, 9); vulm("(",0,5,0,10); vulm("[",0,5,0,11);
    vulm(".",3,5,0,12); vulm(",",3,5,0,13); vulm("'",3,5,0,14);
    vulm("\x8b",0,5,0,15); vulm("j",1,5,0,16); vulm("\x60",0,5,0,17);

    vulm("i",2,6,1, 0); vulm("\x89",1,6,1, 1); vulm("c",1,6,1, 2);
    vulm("s",0,6,1, 3); vulm("f",0,6,1, 4); vulm("t",0,6,1, 5);
    vulm("e",0,6,1, 6); vulm("f",0,6,1, 7); vulm(" ",1,6,1, 8);
    vulm("t",0,6,1, 9); vulm("-",0,6,1,10); vulm(")",0,6,1,11);
    vulm("i",3,6,1,12); vulm("l",3,6,1,13); vulm("f",3,6,1,14);
    vulm("t",3,6,1,15); vulm("j",3,6,1,16);
    vulm("/",0,6,1,17); vulm("[",3,6,1,18);


    vulm("j",2,7,2, 0); vulm("s",2,7,2, 1); vulm("\x94",1,7,2, 2);
    vulm("v",1,7,2, 3); vulm("y",1,7,2, 4); vulm("g",1,7,2, 5);
    vulm("r",1,7,2, 6); vulm("o",1,7,2, 7); vulm("r",0,7,2, 8);
    vulm("s",0,7,2, 9); vulm("I",0,7,2,10); vulm(":",0,7,2,11);
    vulm(";",0,7,2,12); vulm("!",0,7,2,13); vulm("r",3,7,2,14);
    vulm("l",3,7,2,15); vulm("-",3,7,2,16);
    vulm(":",3,7,2,17); vulm(";",3,7,2,18); vulm("!",3,7,2,19);
    vulm("[",3,7,2,20); vulm("]",3,7,2,21); vulm("\x22",1,7,2,22);
    vulm("\f8",0,7,2,23); vulm("(",0,7,2,24);

    vulm("p",2,8,3, 0); vulm("J",1,8,3, 1); vulm("I",1,8,3, 2);
    vulm("q",1,8,3, 3); vulm("b",1,8,3, 4); vulm("d",1,8,3, 5);
    vulm("h",1,8,3, 6); vulm("n",1,8,3, 7); vulm("a",1,8,3, 8);
    vulm("u",1,8,3, 9); vulm("a",0,8,3,10); vulm("e",0,8,3,11);
    vulm("c",0,8,3,12); vulm("z",0,8,3,13); vulm("\x84",0,8,3,14);
    vulm("s",3,8,3,15); vulm("J",3,8,3,16);
    vulm(":",1,8,3,17); vulm(";",1,8,3,18); vulm("\x15",0,8,3,19);

    vulm("y",3,9,4, 0); vulm("b",3,9,4, 1); vulm("l",3,9,4, 2);
    vulm("e",3,9,4, 3); vulm("?",1,9,4, 4); vulm("!",1,9,4, 5);
    vulm("\x98",1,9,4, 6); vulm("p",1,9,4, 7); vulm(" ",2,9,4, 8);
    vulm("J",0,9,4, 9); vulm("3",0,9,4,10); vulm("6",0,9,4,11);
    vulm("9",0,9,4,12); vulm("5",0,9,4,13); vulm("8",0,9,4,14);
    vulm("a",3,9,4,15); vulm("z",3,9,4,16);
    vulm("?",1,9,4,17); vulm("*",1,9,4,18); vulm("(",1,9,4,19);
    vulm("$",1,9,4,20); vulm("\xae",0,9,4,21);
    vulm("\xaf",0,9,4,22); vulm("\xe1",1,9,4,23); vulm("$",0,9,4,24);

    vulm("z",3,9,5, 0); vulm("f",3,9,5, 1); vulm("t",3,9,5, 2);
    vulm("(",1,9,5, 3); vulm("fi",1,9,5, 4); vulm("fl",1,9,5, 5);
    vulm("z",1,9,5, 6); vulm("?",0,9,5, 7); vulm("x",0,9,5, 8);
    vulm("y",0,9,5, 9); vulm("7",0,9,5,10); vulm("4",0,9,5,11);
    vulm("1",0,9,5,12); vulm("0",0,9,5,13); vulm("2",0,9,5,14);
    vulm("e",3,9,5,15); vulm("c",3,9,5,16);
    vulm(",,",3,9,5,17); vulm("$",3,9,5,18); vulm("[",1,9,5,19);
    vulm("]",1,9,5,20);

    vulm("x",3,10,6, 0); vulm("q",3,10,6, 1); vulm("u",3,10,6, 2);
    vulm("o",1,10,6, 3); vulm("S",1,10,6, 4); vulm("k",1,10,6, 5);
    vulm("q",0,10,6, 6); vulm("h",0,10,6, 7); vulm("p",0,10,6, 8);
    vulm("g",0,10,6, 9); vulm("\x98",0,10,6,10); vulm("b",0,10,6,11);
    vulm("ff",0,10,6,12); vulm("fl",0,10,6,13); vulm("fi",0,10,6,14);
    vulm("y",3,10,6,15); vulm("S",3,10,6,16);
    vulm("\x15",3,10,6,17); vulm("\x15",1,10,6,18); vulm("\xd8",0,10,6,19);
    vulm("\xd8",3,10,6,20);

    vulm("v",3,10,7, 0); vulm("c",3,10,7, 1); vulm("r",3,10,7, 2);
    vulm("a",3,10,7, 3); vulm("ff",1,10,7, 4); vulm("S",0,10,7, 5);
    vulm("v",0,10,7, 6); vulm("k",0,10,7, 7); vulm("u",0,10,7, 8);
    vulm("n",0,10,7, 9); vulm("o",0,10,7,10); vulm("d",0,10,7,11);
    vulm("\x94",0,10,7,12); vulm("\x81",0,10,7,13); vulm("o",3,10,7,14);
    vulm("x",3,10,7,15); vulm("v",3,10,7,16);
    vulm("fj",1,10,7,17); vulm("\x91",1,10,7,18); vulm("\xe0",0,10,7,19);
    vulm("fj",0,10,7,20);

    vulm("k",3,11,8, 0); vulm("d",3,11,8, 1); vulm("g",3,11,8, 2);
    vulm("n",3,11,8, 3); vulm("w",1,11,8, 4); vulm("x",1,11,8, 5);
    vulm("F",0,11,8, 6); vulm("P",0,11,8, 7); vulm("u",3,11,8, 8);
    vulm("n",3,11,8, 9); vulm("\x98",3,11,8,10); vulm("g",3,11,8,11);
    vulm("b",3,11,8,12); vulm("d",3,11,8,13); vulm("h",3,11,8,14);
    vulm("k",3,11,8,15); vulm("p",3,11,8,16);
    vulm("\x9d",1,11,8,17); vulm("\x91",0,11,8,18); vulm("q",3,11,8,19);
    vulm("fi",3,11,8,20); vulm("fl",3,11,8,21); vulm("ff",3,11,8,22);
    vulm("\xe1",3,11,8,23); vulm("fj",3,11,8,24);

    vulm("Q",1,14,9, 0); vulm("Y",1,14,9, 1); vulm("K",1,14,9, 2);
    vulm("h",2,12,9, 3); vulm("m",2,12,9, 4); vulm("C",1,14,9, 5);
    vulm("L",1,14,9, 6); vulm("B",0,12,9, 7); vulm("C",0,12,9, 8);
    vulm("L",0,12,9, 9); vulm("F",3,12,9,10); vulm("P",3,12,9,11);
    vulm("O",1,14,9,12); vulm("\x9c",0,12,9,13); vulm("\x80",0,12,9,14);
    vulm("\0",0,12,9,15); vulm("\0",0,12,9,16);

    vulm("ffi",1,13,10, 0); vulm("ffl",1,13,10, 1); vulm("G",1,15,10, 2);
    vulm("T",1,13,10, 3); vulm("Z",1,13,10, 4); vulm("B",1,13,10, 5);
    vulm("P",1,13,10, 6); vulm("U",1,15,10, 7); vulm("m",1,13,10, 8);
    vulm("E",0,13,10, 9); vulm("T",0,13,10,10); vulm("R",0,13,10,11);
    vulm("Z",0,13,10,12); vulm("L",3,13,10,13); vulm("B",3,13,10,14);
    vulm("C",3,13,10,15); vulm("Z",3,13,10,16);
    vulm("fb",1,13,10,17); vulm("fh",1,13,10,18); vulm("\x9c",3,13,10,19);
    vulm("\x91",3,13,10,20);

    vulm("w",3,14,11, 0); vulm("F",1,14,11, 1); vulm("R",1,14,11, 2);
    vulm("V",0,14,11, 3); vulm("Y",0,14,11, 4); vulm("A",0,14,11, 5);
    vulm("U",0,14,11, 6); vulm("w",0,14,11, 7); vulm("A",3,14,11, 8);
    vulm("E",3,14,11, 9); vulm("G",3,14,11,10); vulm("T",3,14,11,11);
    vulm("R",3,14,11,12); vulm("K",3,14,11,13); vulm("V",3,14,11,14);
    vulm("X",3,14,11,15); vulm("Y",3,14,11,16); vulm("\x91",3,14,11,17);

    vulm("ffi",0,15,12, 0); vulm("E",1,15,12, 1); vulm("ffl",0,15,12, 2);
    vulm("Q",0,15,12, 3); vulm("X",0,15,12, 4); vulm("K",0,15,12, 5);
    vulm("D",0,15,12, 6); vulm("G",0,15,12, 7); vulm("H",0,15,12, 8);
    vulm("N",0,15,12, 9); vulm("O",0,15,12,10); vulm("m",0,15,12,11);
    vulm("w",3,15,12,12); vulm("O",3,15,12,13); vulm("D",3,15,12,14);
    vulm("U",3,15,12,15); vulm("Q",3,15,12,16);
    vulm("fk",1,15,12,17); vulm("fb",0,15,12,18); vulm("fh",0,15,12,19);
    vulm("fk",0,15,12,20);

    vulm("fb",3,17,13, 0); vulm("fh",3,17,13, 1); vulm("V",1,17,13, 2);
    vulm("X",1,17,13, 3); vulm("D",1,17,13, 4); vulm("H",1,17,13, 5);
    vulm("N",1,17,13, 6); vulm("A",1,17,13, 7); vulm("M",0,17,13, 8);
    vulm("&",0,17,13, 9); vulm("m",3,17,13,10); vulm("ffi",3,17,13,11);
    vulm("ffl",3,17,13,12); vulm("H",3,17,13,13); vulm("N",3,17,13,14);
    vulm("&",3,17,13,15); vulm("fk",3,17,13,16);

    vulm("\xab",0,18,14, 0); vulm("W",1,18,14, 1); vulm("\xac",0,18,14, 2);
    vulm("M",1,18,14, 3); vulm("*",0,18,14, 4); vulm("W",0,18,14, 5);
    vulm("+",0,18,14, 6); vulm("M",3,18,14, 7); vulm("&",1,18,14, 8);
    vulm("W",3,18,14, 9); vulm("=",0,18,14,10); vulm("--",3,18,14,11);
    vulm("%",0,18,14,12); vulm("--",0,18,14,13); vulm("\0",0,18,14,14);
    vulm("\xf1",0,18,14,15); vulm(" ",3,18,14,16);
    vulm("\x92",0,18,14,17); vulm("\x92",1,18,14,18); vulm("\x91",2,18,14,19);
}



/********************************************************/
/*   allocate records for the matrix                    */
/*                                                      */
/*   1e version: 8-2-2001                               */
/*********************************************************/
void matrix_gereedmaken(void)    /* init matrix pointers */
{
    int i,j;

    for (i=0;i<=15;i++){
       for (j=0;j<=29;j++){
	   /* vrijmaken */
	   /* pointer in array zetten */
	   matrix[16][30] = vrijmaken();
       }
    }
}

/********************************************************/
/*   matrix-inlezen  read matrix from screen            */
/*                                                      */
/*   give back: the "set"  version 8-2-2001             */
/********************************************************/
unsigned int matrix_inlezen(void)    /* read matrix */
{
    int i,j;
    unsigned int set;
    char buf[20];

    cls();
    printf("              Inlezen matrix \n\n");
    getchar();
    for (i=0;i<=15;i++){
       printf("Rij : %2d \n",i+1);
       for (j=0;j<=29;j++){
	   cls();
	   printf("Rij   : %2d \n\n",i+1);
	   printf("Kolom : %c : ",ncols[j]);
	   getchar();
	   /* vrijmaken  + put pointer in array */
	   /* matrix[16][30] = vrijmaken(); */
       }
    }
    return set;
}


void schrijf_matrix()
{
;
}

void display_matrix()
{
    unsigned int ri,cj;
    int diff;
    cls();
    /* naam letter */
    /* set         */
    /* pnt english, pnt didot */
    /* */

    printf("     NI  NL   A   B   C   D   E   F   G   H   I   J   K   L   M   N   O\n");
    printf("\n");
    for (ri=0;ri<=14;ri++){
       printf(" %2d ",wedge[row]);
       for (cj=0;cj<=16;cj++)
	  printf("%3c ",matrix[ri][cj]->ligature);
       printf(" %2d \n",row+1);
       for (cj=0;cj<=16;cj++){
	  diff = ( (matrix[ri][rj] -> width) - wedge[ri] ) ;
	  (diff == 0) ? printf("    ") : printf("%3c ",diff);
       }
       printf("\n");
    }
    getchar();
}

