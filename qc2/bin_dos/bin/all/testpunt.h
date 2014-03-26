/****************************************************************************/
/*                    test programma GLOBALS                                */
/****************************************************************************/
char string[11] = "abcdefghij\0" ;



/****************************************************************************/
/*                      private headers                                     */
/****************************************************************************/

/* structure definitions */

struct m_type {
	unsigned int naam;       /* voor testen routines                */
	char ligature[4];        /* room for 3 chars: ffi, ffl max...   */
	unsigned char kind;      /* roman, italic, small cap, bold      */
	unsigned char width;     /* nominal witdh in units              */
	unsigned char row;       /* row in matrix                       */
	unsigned char col;       /* colom in matrix                     */
				 /* 0-16, 17=> outside matrix !         */
	unsigned char u1;        /* wedge-positions u1/u2               */
	unsigned char u2;        /*                                     */
	unsigned char code[4];   /* the actual code                     */
	struct m_type *_fore;
	struct m_type *_next;
} ;


struct m_type * curs = NULL ;
struct m_type * einde_regel = NULL ;
struct m_type * begin_regel = NULL;

/*$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$*/

/* ********* central memory of the program *** */

struct m_type opslag[500];  /* should be more than sufficient room     */



/*  function-declarations */

void gereedmaken_opslag(void); /* initialiseer voorraad                 */
struct m_type * vrijmaken(void);     /*  haal record uit voorraad              */
struct m_type * achtervoegen(struct m_type *px, struct m_type * einde);
			     /* zet een record achter in de rij */
void terugzetten(struct m_type *px);      /* put record in storage       */

/*  in de rij :
		voegt een record in de rij na het record waarna de cursor
		wijst, en verzet de cursor naar het nieuwe record
*/

void in_de_rij(struct m_type * cur, struct m_type * px);
struct m_type * del ( struct m_type * cur) ;   /* delete record voor de cursor */
struct m_type * backsp( struct m_type * cur);   /* delete record waarnaar de cursor */
										  /* wijst

struct m_type * start_rij( void );     /* start de rij: eerste               */
/*  globals */

/*****  function-definitions *****/

/* gereedmaken_opslag

	= take the memmory fysically in possession

	the compiler, uses the memmory is a very dynamical way
	and you may find the the memmory is spoiled

	It costs some performance, but secures a good behaviour of
	the program

*/

void clear_record(struct m_type * p);

struct m_type *  voeg_toe( char c, struct m_type * cursor );

struct m_type * inkorten(struct m_type *strt);
void show_voorraad(unsigned int start, unsigned int aantal, int r);
void show_rij( struct m_type *cur , int direct );


