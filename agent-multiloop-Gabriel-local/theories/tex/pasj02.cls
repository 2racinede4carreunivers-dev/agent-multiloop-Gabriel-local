%% =============================================  
%% pasj02.cls - version 2.2   (2026 May 6) 
%% =============================================
%%
%% This is file `pasj02.cls',
%% generated with the docstrip utility.
%%
%% The original source files were:
%%
%% pasj.dtx  (with options: `cls,distribution')
%% 
%% IMPORTANT NOTICE:
%% 
%% - The contents of this file is originally managed by GlobalTeX Co., Ltd.
%% - Any modified versions of this file must be renamed
%%   with new filenames distinct from its original name.
%% - You must not distribute this generated file without written permission
%%   of the Astronomical Society of Japan 
%%
\NeedsTeXFormat{LaTeX2e}[1995/12/01]
\ProvidesClass{pasj02}[2026/05/06 v.2.2 Simplified document class for PASJ^^J%
\@spaces\@spaces\@spaces(C) 2026 Astronomical Society of Japan]
\DeclareOption{draft}{\setlength\overfullrule{5pt}}
\DeclareOption{final}{\setlength\overfullrule{0pt}}
\newif\if@restonecol
\DeclareOption{onecolumn}{\@twocolumnfalse}
\DeclareOption{twocolumn}{\@twocolumntrue}
\newif\if@openright
\DeclareOption{openright}{\@openrighttrue}
\DeclareOption{openany}{\@openrightfalse}
\newif\if@proofread
\@proofreadfalse
\DeclareOption{proof}{\@proofreadtrue}
\newif\if@useamsfonts
\@useamsfontsfalse
\DeclareOption{useamsfonts}{\@useamsfontstrue}
\newif\if@pasj@usefigure
\@pasj@usefiguretrue
\DeclareOption{nofigure}{\@pasj@usefigurefalse}
\newif\if@mfastrosym
\@mfastrosymfalse
\DeclareOption{mfastrosym}{\@mfastrosymtrue}
\ExecuteOptions{final,twocolumn,openright}
\ProcessOptions
\@twosidetrue
\def\SetVolumeData#1#2#3{%
   \@tempcnta\year
   \afterassignment\remove@to@nnil
   \count@0#1\relax\@nnil
   \ifnum\count@>\z@ \year\count@ \else \year\@tempcnta \fi
   \def\no{#3}%
   \def\@@vol{#2}}
\def\SetRunningHead#1#2{%
   \def\@Author{#1}%
   \def\@runninghead{#2}}
\def\SetContentsData#1#2{%
   \if@filesw
         \begingroup
         \let\break\robustbreak
         \addcontentsline{toc}{article}{{#1}{#2}{\lett}}%
         \endgroup
   \fi}
\edef\robustbreak{%
   {\noexpand\protect
   \expandafter\noexpand\csname break \endcsname}}
\long\def\title#1{\def\@title{#1}}
\def\author{\@add@author*\relax{}}
\def\@affil{}
\def\affil#1{\xdef\@affil{\ifx\@affil\@empty#1\else\@affil\par#1\fi}}
%%%
\newcount\aucnt
\newcount\tempcount
\newcount\@tempcnta
\def\author#1{\global\advance\aucnt\@ne\expandafter\gdef\csname author\romannumeral\the\aucnt\endcsname{#1}}
\def\printauthor{%
\ifnum\aucnt>\z@%
    \tempcount\z@%
    \@tempcnta=\aucnt%%
    \loop%
    \ifnum\@tempcnta>\z@%
     \advance\tempcount\@ne%
     \csname author\romannumeral\the\tempcount\endcsname%
         \ifnum\aucnt>2%%
	   \ifnum\@tempcnta>\@ne\ifnum\@tempcnta=2\ and\ %%
	   \else, \fi\fi%%
       \else%%
	   \ifnum\@tempcnta>\@ne\ifnum\@tempcnta=2\ and\ %%
	   \else, \fi\fi%%
       \fi%%
       \global\advance\@tempcnta\m@ne%%
    \repeat%
\fi%
}
%%%
%% for ORCID 
\def\@orcid{}%
\def\orcid#1{\xdef\@orcid{\ifx\@orcid\@empty ORCID: #1\else\@orcid,\ #1\fi}}
%%%
\def\@email{}
\def\email#1{\xdef\@email{\ifx\@email\@empty $^{\ast}$E-mail: #1\else\@email,\ #1\fi}}
%%% 
\def\altaffilmark#1{\textsuperscript{\fontfamily{\sfdefault}\selectfont\bfseries#1}}
\def\altemailmark{{\fontfamily{\sfdefault}\selectfont\bfseries\mathversion{bold}$^{, \ast}$}}
\def\altaffiltext#1#2{\protected@xdef\@affil{\ifx\@affil\@empty\@hangfrom{\protect\textsuperscript{#1}}#2\else\@affil\par\@hangfrom{\protect\textsuperscript{#1}}#2\fi}}
%%
\def\and{\@add@author\relax{}{and}}
\def\@add@author{%
   \@ifstar
      {\let\@affil@curr@prefix\@empty
       \let\@affil@curr@break\@affil@break
       \@add@author@}%
      {\let\@affil@curr@prefix\@affil@prefix
       \let\@affil@curr@break\@empty
       \@add@author@}}
\long\def\@add@author@#1#2#3{%
   \let\@tempa\@empty
   \def\@add@author@font{#1}%
   \expandafter\@add@author@loop\@affil@curr@prefix#2#3\\\@nil\\\@gobble\\%
   \@csc@t\@author\@author\@tempa
   \def\@affil@prefix{\\}%
   \let\@affil@break\@affil@break@}
\def\@affil@break@{\@@par}
\long\def\@add@author@loop#1\\#2\\{%
   \def\@tempb{#1}%
   \def\@tempc{#2}%
   \ifx\@tempb\@nnil
      \expandafter\@gobbletwo
   \else
      \expandafter\def\expandafter\@tempb\expandafter{%
         \expandafter\ignorespaces\@tempb\unskip}%
      \@csc@t\@tempb\@add@author@font\@tempb
      \expandafter\def\expandafter\@tempb\expandafter{%
         \expandafter{\@tempb}}%
      \@csc@t\@tempb\@affil@curr@break\@tempb
      \let\@affil@curr@break\@empty
      \ifx\@tempc\@nnil\else
         \def\@tempd{\\}%
         \@csc@t\@tempb\@tempb\@tempd
      \fi
      \@csc@t\@tempa\@tempa\@tempb
      \expandafter\@add@author@loop
   \fi
   #2\\}
\def\Received#1{\def\rdate{#1}}
\def\Accepted#1{\def\adate{#1}}
\def\Published#1{\def\pdate{#1}}
\long\def\KeyWords#1{\def\@keywords{#1}}
\let\kword\KeyWords
%
%%% initialize some commands used for producing head/foot
\let\@Author\relax
\let\@runninghead\relax
\let\@keywords\@empty
\let\@title\@empty
\let\@author\@empty
\let\@affil@prefix\@empty
\let\@affil@break\@empty
\let\@@vol\@empty
\let\no\@empty
\let\rdate\@empty
\let\adate\@empty
\let\pdate\@empty
\def\pageSTART{\thepage}
\def\pageEND{{\bfseries??}}
\def\@@pageEND{10000}
\let\@plateno\@empty
\let\@firstplate\@empty
\let\@lastplate\@empty
\edef\plateid{\string\plateid}
\def\@ptsize{0}
%
%%% font setting (optional)
\openin\@inputcheck pasjfont.sty\relax
\ifeof\@inputcheck \let\@tempa\relax
\else              \def\@tempa{\@@input pasjfont.sty\relax}\fi
\closein\@inputcheck
\@tempa
\@ifundefined{@astrofont}{\let\@astrofont\@empty}{}
%
%%% font size
\newdimen\defaultbaselineskip
\defaultbaselineskip 12\p@
\DeclareRobustCommand*\normalsize{%
   \@setfontsize\normalsize\@size@for@normalsize\defaultbaselineskip
   \abovedisplayskip 6\p@ \@plus2\p@ \@minus5\p@
   \belowdisplayskip \abovedisplayskip
   \abovedisplayshortskip \z@ \@plus3\p@
   \belowdisplayshortskip 6\p@ \@plus3\p@ \@minus3\p@
   \let\@listi\@listI}
\DeclareRobustCommand*\small{%
   \@setfontsize\small\@size@for@small{10.5}%
   \abovedisplayskip 5.5\p@ \@plus3\p@ \@minus4\p@
   \belowdisplayskip \abovedisplayskip
   \abovedisplayshortskip \z@ \@plus2\p@
   \belowdisplayshortskip 4\p@ \@plus2\p@ \@minus2\p@
   \def\@listi{%
      \leftmargin\leftmargini
      \topsep 6\p@ \@plus\p@ \@minus\p@
      \parsep  \z@ \@plus\p@ \@minus\p@
      \itemsep \parsep}}
\DeclareRobustCommand*\footnotesize{%
   \@setfontsize\footnotesize\@size@for@footnotesize{9.5}%
   \abovedisplayskip 4.75\p@ \@plus2\p@ \@minus4\p@
   \belowdisplayskip \abovedisplayskip
   \abovedisplayshortskip \z@ \@plus\p@
   \belowdisplayshortskip 3\p@ \@plus\p@ \@minus2\p@
   \def\@listi{%
      \leftmargin\leftmargini
      \topsep 6\p@ \@plus\p@ \@minus\p@
      \parsep  \z@ \@plus\p@ \@minus\p@
      \itemsep \parsep}}
\DeclareRobustCommand*\scriptsize{%
   \@setfontsize\scriptsize\@size@for@scriptsize\@viiipt}
\DeclareRobustCommand*\tiny{\@setfontsize\tiny\@size@for@tiny\@vipt}
\DeclareRobustCommand*\large{\@setfontsize\large\@size@for@large{14}}
\DeclareRobustCommand*\Large{\@setfontsize\Large\@size@for@Large{18}}
\DeclareRobustCommand*\LARGE{\@setfontsize\LARGE\@size@for@LARGE{22}}
\DeclareRobustCommand*\huge{\@setfontsize\huge\@size@for@huge{25}}
\DeclareRobustCommand*\Huge{\@setfontsize\Huge\@size@for@Huge{30}}
%
%%% page size/margins etc.
\paperwidth     210mm
\paperheight    276mm
\textheight     56.0pc %%% previous value: 655.5pt, 55.5pc
\textwidth      42.2pc
\columnsep       6.35mm%18pt
\columnseprule    \z@
\def\@set@sidemargins{%
   \@ifstar{\@tempswafalse\@set@sidemargins@}%
           {\@tempswatrue\@set@sidemargins@}}
\def\@set@sidemargins@#1{%
   \dimen@#1\relax
   \ifdim\dimen@>\z@
      \evensidemargin\dimen@
      \if@tempswa
         \oddsidemargin\paperwidth
         \advance\oddsidemargin-\textwidth
         \advance\oddsidemargin-\evensidemargin
      \else
         \oddsidemargin\evensidemargin
      \fi
   \else
      \dimen@\paperwidth
      \advance\dimen@-\textwidth
      \divide\dimen@\tw@
      \oddsidemargin\dimen@
      \evensidemargin\dimen@
   \fi
   \advance\oddsidemargin  -1in
   \advance\evensidemargin -1in
   \relax}
%% \@set@sidemargins{55.7756pt}
%% \advance\topmargin -1in
%%%

\setlength\topmargin{28pt}
\setlength\oddsidemargin   {48pt}%{55.7756pt}
\setlength\evensidemargin\paperwidth
\addtolength\evensidemargin{-\textwidth}
\addtolength\evensidemargin{-\oddsidemargin}
%
\setlength\headheight{5.5\p@}% 
\setlength\headsep   {21.15pt}% \typeheight - \textheight - \headheight
\setlength\topskip   {7.15\p@}
%%  
\advance\oddsidemargin  -1in
\advance\evensidemargin -1in
\advance\topmargin  -1in
\advance\textheight-36.5pt
%%%
\@ifundefined{mathindent}{\newskip\mathindent}{}
\def\usetenpoint{%
   \def\@ptsize{0}%
   \def\@size@for@tiny{\@vpt}%
   \def\@size@for@scriptsize{\@viipt}%
   \def\@size@for@footnotesize{\@viiipt}%
   \def\@size@for@small{\@ixpt}%
   \def\@size@for@normalsize{9.25}%
   \def\@size@for@large{\@xiipt}%
   \def\@size@for@Large{\@xivpt}%
   \def\@size@for@LARGE{\@xviipt}%
   \def\@size@for@huge{\@xxpt}%
   \def\@size@for@Huge{\@xxvpt}%
   \normalsize}
\def\tenpoint{%
   \usetenpoint
   %\headsep .8pc \advance\headsep 10\p@ \advance\headsep-\topskip
   \parindent  10pt
   \mathindent 0pc
   \relax}
\def\useelevenpoint{%
   \def\@ptsize{1}%
   \def\@size@for@tiny{\@vipt}%
   \def\@size@for@scriptsize{\@viiipt}%
   \def\@size@for@footnotesize{\@ixpt}%
   \def\@size@for@small{\@xpt}%
   \def\@size@for@normalsize{\@xipt}%
   \def\@size@for@large{\@xiipt}%
   \def\@size@for@Large{\@xivpt}%
   \def\@size@for@LARGE{\@xviipt}%
   \def\@size@for@huge{\@xxpt}%
   \def\@size@for@Huge{\@xxvpt}%
   \normalsize}
\def\elevenpoint{%
   \useelevenpoint
   \headsep 35\p@ \advance\headsep 10\p@ \advance\headsep-\topskip
   \footskip    40\p@
   \footnotesep 12\p@
   \parindent  3em
   \mathindent 5em
   \relax}
\def\usetwelvepoint{%
   \def\@ptsize{2}%
   \def\@size@for@tiny{\@vipt}%
   \def\@size@for@scriptsize{\@viiipt}%
   \def\@size@for@footnotesize{\@xpt}%
   \def\@size@for@small{\@xipt}%
   \def\@size@for@normalsize{\@xiipt}%
   \def\@size@for@large{\@xivpt}%
   \def\@size@for@Large{\@xviipt}%
   \def\@size@for@LARGE{\@xxpt}%
   \def\@size@for@huge{\@xxvpt}%
   \def\@size@for@Huge{\@xxvpt}%
   \normalsize}
\def\twelvepoint{%
   \usetwelvepoint
   \headsep 35\p@ \advance\headsep 10\p@ \advance\headsep-\topskip
   \footskip    40\p@
   \footnotesep 12\p@
   \parindent  3em
   \mathindent 5em
   \relax}
\def\draft{%
   \@proofreadtrue
   \twelvepoint
   \def\ps@draft{%
      \let\@mkboth\@gobbletwo
      \def\@oddfoot{\hfil{\normalsize\normalfont\lett\thepage}\hfil}%
      \def\@evenfoot{\hfil{\normalsize\normalfont\lett\thepage}\hfil}%
      \def\@oddhead{\@set@proofmark\hfil}%
      \let\@evenhead\@oddhead}%
   \pagestyle{headings}%\pagestyle{draft}%
   %\let\ps@firstpage\ps@draft
   \textwidth  170mm
   \topmargin  -5.4mm %%% 20mm - 1in
   \advance\topmargin-\headheight \advance\topmargin-\headsep
   \textheight 237mm
   \@set@sidemargins\z@ %%% \z@ ==> left margin = right margin
   \onecolumn
   \linespread{1.5}%
   \normalsize
   \footskip\baselineskip\relax
   \advance\textheight-\footskip}
\usetenpoint

%% \headsep .8pc \advance\headsep 10\p@ \advance\headsep-\topskip
\parindent  10pt
\mathindent 0pc
%% \topskip         \defaultbaselineskip
%% \advance\topskip-.05\p@
%% \headsep         .8pc
%% \headheight      12\p@
%% \advance\headsep 10\p@
%% \advance\headsep-\topskip %%% \headsep + \topskip = .8pc + 10pt
%% \footskip       .35in
%% \maxdepth        4\p@
%% \marginparwidth  48\p@
%% \marginparsep    10\p@
%% \marginparpush    5\p@
%% \footnotesep   6.65\p@
%% \skip\footins     9\p@ \@plus 4\p@ \@minus 2\p@
%% \skip\@mpfootins = \skip\footins
\arraycolsep      5\p@
\tabcolsep        6\p@
\arrayrulewidth  .4\p@
\doublerulesep    2\p@
\tabbingsep        \labelsep
%% \fboxsep          3\p@
%% \fboxrule        .4\p@
%% \floatsep        12\p@ \@plus 2\p@ \@minus 2\p@
%% \textfloatsep    12\p@ \@plus 2\p@ \@minus 4\p@
%% \intextsep       12\p@ \@plus 2\p@ \@minus 2\p@
%% \dblfloatsep     12\p@ \@plus 2\p@ \@minus 2\p@
%% \dbltextfloatsep 12\p@ \@plus 2\p@ %%% \@minus 4\p@
%% \@fptop            \z@
%% \@fpsep           8\p@ \@plus 2fil
%% \@fpbot            \z@ \@plus 1fil
%% \@dblfptop         \z@ \@plus 1fil
%% \@dblfpsep        8\p@ \@plus 2fil
%% \@dblfpbot         \z@ \@plus 1fil
%% \lineskip          \p@
%% \normallineskip    \p@
%% \parskip           \z@ \@plus \p@
%% \def\baselinestretch{}%%% empty ==> single space
%% \dimen@\defaultbaselineskip\relax
%% \smallskipamount .25\dimen@ \@plus 1\p@ \@minus 1\p@
%% \medskipamount    .5\dimen@ \@plus 2\p@ \@minus 2\p@
%% \bigskipamount      \dimen@ \@plus 4\p@ \@minus 4\p@
%% \@lowpenalty   51
%% \@medpenalty  151
%% \@highpenalty 301
%
%%% lists
\def\@listi{%
   \leftmargin\leftmargini
   \labelwidth\leftmargini
   \advance\labelwidth-\labelsep
   \parsep   \z@ \@plus \p@
   \topsep  .5\defaultbaselineskip \@plus \p@ \@minus \p@
   \itemsep  \z@ \@plus \p@ \@minus \p@}
\let\@listI\@listi
\@listi
\def\@listii{%
   \leftmargin\leftmarginii
   \labelwidth\leftmarginii
   \advance\labelwidth-\labelsep
   \topsep  .5\defaultbaselineskip \@plus \p@ \@minus \p@
   \parsep   \z@ \@plus \p@
   \itemsep  \parsep}
\def\@listiii{%
   \leftmargin\leftmarginiii
   \labelwidth\leftmarginiii
   \advance\labelwidth-\labelsep
   \topsep     \z@ \@plus \p@ \@minus \p@
   \parsep     \z@ \@plus \p@
   \partopsep  \z@ \@plus \z@ \@minus \p@
   \itemsep    \topsep}
\def\@listiv{%
   \leftmargin\leftmarginiv
   \labelwidth\leftmarginiv
   \advance\labelwidth-\labelsep}
\def\@listv{%
   \leftmargin\leftmarginv
   \labelwidth\leftmarginv
   \advance\labelwidth-\labelsep}
\def\@listvi{%
   \leftmargin\leftmarginvi
   \labelwidth\leftmarginvi
   \advance\labelwidth-\labelsep}
\@beginparpenalty -\@lowpenalty
\@endparpenalty   -\@lowpenalty
\@itempenalty     -\@lowpenalty
\partopsep         \z@ \@plus 1\p@ \@minus 1\p@
\leftmargini     25\p@
\leftmarginii    22\p@
\leftmarginiii 18.7\p@
\leftmarginiv    17\p@
\leftmarginv     10\p@
\leftmarginvi    10\p@
\leftmargin\leftmargini
\labelsep         5\p@
\labelwidth\leftmargini
\advance\labelwidth-\labelsep
%
\def\itemize{\setlength\leftmargini{1em}\labelsep5pt%
  \ifnum \@itemdepth >\thr@@\@toodeep\else
    \advance\@itemdepth\@ne
    \edef\@itemitem{labelitem\romannumeral\the\@itemdepth}%
    \expandafter
    \list
      \csname\@itemitem\endcsname
      {\setlength\leftmarginii{1.1em}\itemsep0pt\ifnum \@listdepth >1\topsep0pt\else\topsep3pt\fi\parsep0pt\parskip0pt\def\makelabel##1{\hss\llap{##1}}}%
  \fi}
%%
\def\enumerate{\setlength\leftmargini{1.25em}%
  \ifnum \@enumdepth >\thr@@\@toodeep\else
    \advance\@enumdepth\@ne
    \edef\@enumctr{enum\romannumeral\the\@enumdepth}%
      \expandafter
      \list
        \csname label\@enumctr\endcsname
        {\setlength\leftmarginii{1.7em}\itemsep0pt\ifnum \@listdepth >1\topsep0pt\else\topsep3pt\fi\parsep0pt\parskip0pt\usecounter\@enumctr\def\makelabel##1{\hss\llap{##1}}}%
  \fi}
%%
\newenvironment{unnumlist}{\list{}{\itemsep0pt\parsep0pt\parskip0pt\partopsep0pt\leftmargin4mm\itemindent-4mm}}{\endlist}%
%%% itemize/enumerate
\def\theenumi{\@arabic\c@enumi}
\def\labelenumi{\theenumi.}
\def\theenumii{\@alph\c@enumii}
\def\labelenumii{(\theenumii)}
\def\p@enumii{\theenumi}
\def\theenumiii{\@roman\c@enumiii}
\def\labelenumiii{\theenumiii.}
\def\p@enumiii{\theenumi(\theenumii)}
\def\theenumiv{\@Alph\c@enumiv}
\def\labelenumiv{\theenumiv.}
\def\p@enumiv{\p@enumiii\theenumiii}
\def\labelitemi{\textbullet}
\def\labelitemii{\normalfont\bfseries \textendash}
\def\labelitemiii{\textasteriskcentered}
\def\labelitemiv{\textperiodcentered}
\def\@doendpe{%
   \@endpetrue
   \def\par{%
      \@restorepar
      \everypar{%
         \if@nobreak\else \clubpenalty\@clubpenalty \fi
         \everypar{}}%
      \par\@endpefalse}%
   \everypar{%
      {\setbox\z@\lastbox}%
      \if@nobreak\else \clubpenalty\@clubpenalty \fi
      \everypar{}%
      \@endpefalse}}
\def\verse{%
   \let\\\@centercr
   \list{}{%
      \itemsep      \z@
      \itemindent   -1.5em
      \listparindent\itemindent
      \rightmargin  \leftmargin
      \advance\leftmargin 1.5em}%
   \item\relax}
\def\endverse{\endlist}
\def\quotation{%
   \list{}{%
      \listparindent 1.5em
      \itemindent    \listparindent
      \rightmargin   \leftmargin
      \parsep        \z@ \@plus\p@}%
   \item\relax}
\def\endquotation{\endlist}
\def\quote{\list{}{}\item\relax}
\def\endquote{\endlist}
\def\description{%
   \list{}{%
      \labelwidth\z@
      \itemindent-\leftmargin
      \let\makelabel\descriptionlabel}}
\def\enddescription{\endlist}
\def\descriptionlabel#1{\hspace\labelsep\normalfont\bfseries #1}
%
%%% titlepage
\def\titlepage{%
   \cleardoublepage
   \if@twocolumn \@restonecoltrue\onecolumn
   \else         \@restonecolfalse          \fi
   \thispagestyle{empty}%
   \setcounter{page}\z@}%
\def\endtitlepage{\if@restonecol \twocolumn \else \newpage \fi}
\let\@saved@minipage\minipage
\def\minipage{\let\footnoterule\@empty\@saved@minipage}
%
%%% sectioning
\setcounter{secnumdepth}{4}
\global\let\cl@@article\@empty
\newcounter{part}
\@addtoreset{part}{@article}
\newcounter{chapter}
\@addtoreset{chapter}{@article}
\newcounter{section}[chapter]
\@addtoreset{section}{@article}
\newcounter{subsection}[section]
\@addtoreset{subsection}{@article}
\newcounter{subsubsection}[subsection]
\@addtoreset{subsubsection}{@article}
\newcounter{paragraph}[subsubsection]
\@addtoreset{paragraph}{@article}
\newcounter{subparagraph}[paragraph]
\@addtoreset{subparagraph}{@article}
\def\thepart{\@Roman\c@part}
\def\thechapter{\@arabic\c@chapter}
\def\thesection{\@arabic\c@section}
\def\thesubsection{\thesection.\@arabic\c@subsection}
\def\thesubsubsection{\thesubsection.\@arabic\c@subsubsection}
\def\theparagraph{\thesubsubsection.\@arabic\c@paragraph}
\def\thesubparagraph{\theparagraph.\@arabic\c@subparagraph}
\def\@chapapp{\chaptername}
\def\part{%
   \@startsection{part}{-1}{\z@}%
      {\defaultbaselineskip \@plus  1ex \@minus .2ex}%
      {\defaultbaselineskip \@plus .2ex}%
      {\normalfont\large\bfseries\boldmath}}
\let\partmark\@gobble
\def\chapter{%
   \@startsection{chapter}{0}{\z@}%
      {\defaultbaselineskip \@plus 1ex \@minus .2ex}%
      {\defaultbaselineskip \@plus .2ex}%
      {\normalfont\large\bfseries\boldmath}}
\let\chaptermark\@gobble
\def\section{%
   \@startsection{section}{1}{\z@}%
      {-22pt \@plus -.2pt \@minus -.2pt}%
      {4pt}%
      {\sectionfont\boldmath}}
\let\sectionmark\@gobble
\def\subsection@old{%
   \if@aftersection
      \if@twocolumn \vspace{-.5\defaultbaselineskip}\fi
      \expandafter\subsection@a
   \else
      \if@noskipsec \leavevmode \fi
      \ifhmode \unskip\par \fi
      \if@nobreak \nobreak \else \penalty-\@lowpenalty \fi
      \if@twocolumn
         \@nobreaktrue
         \vspace{.5\defaultbaselineskip}%%% modified 2003/7/16
      \else
         \addvspace{.5\defaultbaselineskip}%
      \fi
      \expandafter\subsection@b
   \fi}
\newcommand\subsection{\@startsection{subsection}{2}{\z@}{-20pt \@plus -.2pt \@minus -.2pt}{2pt}{\subsectionfont}}% 4pt --> 2pt 
\def\subsection@a{%
   \@startsection{subsection}{2}{\z@}%
      {.5\defaultbaselineskip \@minus .1ex}%
      {.5\defaultbaselineskip \@minus .1ex}%
      {\normalfont\normalsize\itshape}}
\def\subsection@b{%
   \@startsection{subsection}{2}{\z@}%
      {1sp}%
      {.5\defaultbaselineskip \@minus .1ex}%
      {\subsectionfont}}
\let\subsectionmark\@gobble
\def\subsubsection{%
   \@startsection{subsubsection}{3}{\z@}%
      {-13pt \@plus -.2pt \@minus -.2pt}%%% modified
      {.00001pt}%
      {\subsubsectionfont}}
\let\subsubsectionmark\@gobble
\def\paragraph{%
   \@startsection{paragraph}{4}{\z@}%
      {13pt \@plus 2pt \@minus .2pt}%{\defaultbaselineskip \@minus .1ex}%
      {-.5em}{\paragraphfont}}
\let\paragraphmark\@gobble
\def\subparagraph{%
   \@startsection{subparagraph}{5}{\z@}%
      {13pt \@plus 2pt \@minus .2pt}%
      {-.5em}{\subparagraphfont}}
\let\subparagraphmark\@gobble
\def\@startsection#1#2#3#4#5#6{%
   \if@noskipsec \leavevmode \fi
   \par
   \@tempskipa #4\relax
   \@afterindenttrue
   \ifdim \@tempskipa <\z@
      \@tempskipa -\@tempskipa \@afterindentfalse
   \fi
   \if@nobreak
      \everypar{}%
   \else
      \addpenalty\@secpenalty\addvspace\@tempskipa
   \fi
   \@ifstar
     {\@ssect{#1}{#3}{#4}{#5}{#6}}%
     {\@dblarg{\@sect{#1}{#2}{#3}{#4}{#5}{#6}}}}
\def\@sect#1#2#3#4#5#6[#7]#8{%
   \if@in@appendix
      \ifnum#2>\@ne %%% subsection, subsubsection, ...
         \def\@sectitle@prefix{A.}%
      \else
         \def\@sectitle@prefix{\appendixname\space}%
      \fi
   \else
      \let\@sectitle@prefix\@empty
   \fi
   \ifnum #2>\c@secnumdepth
      \let\@svsec\@empty
      \let\@seccnt@suffix\@empty
   \else
      \refstepcounter{#1}%
      \ifnum#2<\z@%%% \part
         \let\@seccnt@suffix\@empty
      \else       %%% otherwise
         \def\@seccnt@suffix{}%
      \fi
      \protected@edef\@svsec{\@seccntformat{#1}\relax}%
   \fi
   \@tempskipa #5\relax
   \ifdim \@tempskipa>\z@
      \begingroup
         #6{\if@in@appendix
               \@hangfrom{\hskip #3\relax}%
               \@sectitle@prefix\@svsec
            \else
               \@hangfrom{\hskip #3\relax\@svsec}%
            \fi
            \interlinepenalty \@M #8\@@par}%
      \endgroup
%%%      \csname #1mark\endcsname{#7}%
      \addcontentsline{toc}{#1}{%
         \protect\numberline{%
            \@sectitle@prefix
            \csname the#1\endcsname\@seccnt@suffix}%
            #7}%
   \else
      \def\@svsechd{%
         #6{\hskip #3\relax \@svsec #8.}%
%%%         \csname #1mark\endcsname{#7}%
         \addcontentsline{toc}{#1}{%
            \protect\numberline{%
               \@sectitle@prefix
               \csname the#1\endcsname\@seccnt@suffix}%
               #7}%
      }%
   \fi
   \ifnum#2<\tw@ \@aftersectiontrue \else \@aftersectionfalse \fi
   \@xsect{#5}}
\def\@ssect#1#2#3#4#5#6{%
   \@tempskipa #4\relax
   \let\@sectitle@prefix\@empty
   \if@in@appendix
      \def\@tempa{#1}%
      \def\@tempb{section}%
      \ifx\@tempa\@tempb \def\@sectitle@prefix{\appendixname.\quad}\fi%%% modified 2003/7/16+++
   \fi
   \ifdim \@tempskipa>\z@
      \begingroup
         #5{\@hangfrom{\hskip #2}%
            \interlinepenalty \@M
            \if@in@appendix \@sectitle@prefix \fi
            #6\@@par}%
      \endgroup
      \addcontentsline{toc}{#1}{%
         \ifx\@sectitle@prefix\@empty\else
            \protect\numberline{\@sectitle@prefix}%
         \fi
         #6}%
   \else
      \def\@svsechd{%
         #5{\hskip #2\relax
            \if@in@appendix \@sectitle@prefix \fi
            #6}%
         \addcontentsline{toc}{#1}{%
            \ifx\@sectitle@prefix\@empty\else
               \protect\numberline{\@sectitle@prefix}%
            \fi
            #6}%
      }%
   \fi
   \def\@tempa{#1}%
   \def\@tempb{section}%
   \ifx\@tempa\@tempb \@aftersectiontrue \else \@aftersectionfalse \fi
   \@xsect{#4}}
\def\@seccntformat#1{\csname the#1\endcsname\@seccnt@suffix\enspace}
\def\@aftersectiontrue{\global\let\if@aftersection\iftrue}
\def\@aftersectionfalse{\global\let\if@aftersection\iffalse}
\@aftersectionfalse
\def\@afterheading{%
   \@nobreaktrue
   \everypar{%
      \@aftersectionfalse
      \if@nobreak
         \@nobreakfalse
         \clubpenalty \@M
         \if@afterindent \else
           {\setbox\z@\lastbox}%
         \fi
      \else
         \clubpenalty \@clubpenalty
         \everypar{}%
      \fi}}
%
%%% appendix
\newif\if@in@appendix
\global\@in@appendixfalse
\def\appendix{%
   \par
   \@in@appendixtrue
   \setcounter{chapter}{0}%
   \setcounter{section}{0}%
   \setcounter{equation}{0}%
   \def\@chapapp{\appendixname}%
   \def\thechapter{\@Alph\c@chapter}%
   \def\theequation{A\@arabic\c@equation}}
%
%%% equation number
\@addtoreset{equation}{@article}
\def\theequation{\@arabic\c@equation}
%
%%% float placement parameters
\setcounter{topnumber}{2}
\def\topfraction{.9}
\setcounter{bottomnumber}{1}
\def\bottomfraction{.3}
\setcounter{totalnumber}{3}
\def\textfraction{.1}
\def\floatpagefraction{.7}
\setcounter{dbltopnumber}{2}
\def\dbltopfraction{.9}
\def\dblfloatpagefraction{.7}
%
%%% floats
%%% floats
\newcounter{figure}
\@addtoreset{figure}{@article}
\def\thefigure{\@arabic\c@figure}
\def\fps@figure{tbp}
\def\ftype@figure{1}
\def\ext@figure{lof}
\def\fnum@figure{\figurename~\thefigure}
\def\figure@caption@shape{\bfseries}
\def\figure{\@float{figure}}
\def\endfigure{\end@float}
\@namedef{figure*}{\@dblfloat{figure}}
\@namedef{endfigure*}{\end@dblfloat}
\newcounter{table}
\@addtoreset{table}{@article}
\def\thetable{\@arabic\c@table}
\def\fps@table{tbp}
\def\ftype@table{2}
\def\ext@table{lot}
\def\fnum@table{\tablename~\thetable}
\def\table@caption@shape{\bfseries}
\def\table{\@float{table}}
\def\endtable{\end@float}
\@namedef{table*}{\@dblfloat{table}}
\@namedef{endtable*}{\end@dblfloat}
\let\@@dblfloat\@dblfloat
\def\@xfloat#1[#2]{%
   \@nodocument
   \def\@captype{#1}%
   \csname @set@captionskip@for@\@captype\endcsname
   \def\@fps{#2}%
   \@onelevel@sanitize\@fps
   \def\reserved@b{!}%
   \ifx\reserved@b\@fps
      \@fpsadddefault
   \else
      \ifx\@fps\@empty \@fpsadddefault \fi
   \fi
   \ifhmode
      \@bsphack
      \@floatpenalty -\@Mii
   \else
      \@floatpenalty-\@Miii
   \fi
   \ifinner
      \@parmoderr\@floatpenalty\z@
   \else
      \@next\@currbox\@freelist
        {\@read@fps@position
         \global \count\@currbox \@tempcnta}%
         \@fltovf
   \fi
   \global\setbox\@currbox
      \color@vbox
         \normalcolor
         \vbox \bgroup
            \hsize\columnwidth
            \@parboxrestore
            \@floatboxreset}
\def\@read@fps@position{%
   \@tempcnta \sixt@@n
   \expandafter\@tfor\expandafter\reserved@a\expandafter:\expandafter=%
      \@fps\do{%
         \if \reserved@a h%
            \ifodd\@tempcnta\else \advance\@tempcnta\@ne \fi
         \fi
         \if \reserved@a t%
            \@setfpsbit \tw@
         \fi
         \if \reserved@a b%
            \@setfpsbit 4%
         \fi
         \if \reserved@a p%
            \@setfpsbit 8%
         \fi
         \if \reserved@a !%
            \ifnum \@tempcnta>15
               \advance\@tempcnta -\sixt@@n\relax
            \fi
         \fi}%
   \@tempcntb\csname ftype@\@captype\endcsname
   \multiply \@tempcntb \@xxxii
   \advance \@tempcnta \@tempcntb}
\let\end@@dblfloat\end@dblfloat
\def\@extrafloats{48}
\count@\z@
\@whilenum\@extrafloats>\count@\do{%
   \advance\count@\@ne
   \expandafter\newinsert\csname bx@\romannumeral\count@\endcsname
   \expandafter\@cons\expandafter\@freelist
      \csname bx@\romannumeral\count@\endcsname}%
%
%%% \@makecaption
\newlength\abovecaptionskip
\newlength\belowcaptionskip
\def\@set@captionskip@for@figure{%
   \abovecaptionskip -.5\p@
   \belowcaptionskip   \z@}
\def\@set@captionskip@for@table{%
   \abovecaptionskip   \z@
   \belowcaptionskip  0\p@
   \if@proofread \usetenpoint \fi}
\def\captionsidemargin{12pt}
\def\caption{%
   \ifx\@captype\@undefined
      \@latex@error{\noexpand\caption outside float}\@ehd
      \expandafter\@gobble
   \else
      \expandafter\@firstofone
   \fi
   {\@ifnextchar[\@caption@with@option\@caption@without@option}}
\def\@caption@with@option[#1]{%
   \protected@edef\@currentlabel{#1}%
   \@makecaption{\csname\@captype name\endcsname~#1}}
\def\@caption@without@option{%
   \refstepcounter\@captype
   \@makecaption{\csname fnum@\@captype\endcsname}}
\long\def\@caption#1#2{%
   \par
   \begingroup
   \@parboxrestore
   \if@minipage \@setminipage \fi
   \@makecaption{#1}{\ignorespaces #2}\par
   \endgroup}
\long\def\@makecaption#1#2{%
   \ifhmode \unskip\par \fi
   \vskip\abovecaptionskip
   \begingroup
   \def\@tempa{table}%
   \dimen@\topskip
   \ifx\@captype\@tempa
      \edef\@caption@strut{%
         \noexpand\nobreak
         \noexpand\rule\z@{\the\dimen@}}%
   \else
      \let\@caption@strut\@empty
   \fi
   {\ifx\@captype\@tempa\tablecaptionfont\else\figcaptionfont\fi
      \mbox{\@nameuse{\@captype @caption@shape}#1. }%
      \@caption@strut\nobreak
      #2\par}%
   \@tempdima\captionsidemargin\relax
   \@tempdima-2\@tempdima \advance\@tempdima\hsize
   \ifdim \wd\@tempboxa>\@tempdima
     \leftskip\captionsidemargin\relax
     \rightskip\leftskip
     \noindent
     \unhbox\@tempboxa\par
  \else
     \global \@minipagefalse
     \hbox to\hsize{\hfil\box\@tempboxa\hfil}%
  \fi
  \endgroup
  \vskip\belowcaptionskip}
\let\@sharp\relax
\newdimen\@lt@hsize
\newdimen\@lt@caption@hsize
\newbox\@lt@currbox
\newbox\@lt@head
\newbox\@lt@firsthead
\newbox\@lt@foot
\newbox\@lt@lastfoot
\newbox\@lt@prevline
\newbox\@lt@captionbox
\newdimen\@lt@goalsize
\newdimen\@lt@doublerulesep
\newcount\@lt@id
\newcount\@lt@colcnt
\newcount\@lt@maxcols
\newif\if@lt@nocaption
\newif\if@lt@usecaption
\global\@lt@id\z@
\def\longtable{\@lt@usecaptiontrue\@longtable}
\@namedef{longtable*}{\@lt@usecaptionfalse\@longtable}
\def\@longtable{%
   \ifhmode \unskip\par \fi
   \global\advance\@lt@id\@ne
   \def\@captype{table}%
   \@ifnextchar[\@@longtable{\@@longtable[t]}}
\def\@@longtable[#1]#2{%
   \def\@lt@firstposition{#1}%
   \@lt@hsize\textwidth
   \@lt@caption@hsize\textwidth
   \@lt@doublerulesep\doublerulesep
   \advance\@lt@doublerulesep-\arrayrulewidth
   \let\@preamble\@empty
   \protected@edef\@tempa{#2}%
   \expandafter\@lt@expast\@tempa*0x\@nnil
   \expandafter\@lt@mkpream\@preamble\@nnil
   \@lt@init
   \let\@lt@preamble\@preamble
   \@lt@starttabular}

\def\endlongtable{%
   \@lt@endtabular\@empty
   \@lt@output@tabular\@lt@lastfoot
   \if@lt@usecaption
      \if@lt@nocaption
         \@lt@warning{There is no caption for this tabular.}%
      \fi
   \fi
   \@lt@write@boxsize}
\@namedef{endlongtable*}{%
   \@lt@endtabular\@empty
   \@lt@output@tabular\@lt@lastfoot
   \@lt@write@boxsize}
\def\@lt@warning#1{\typeout{^^JWarning [longtable:\the\@lt@id]: #1}}
\def\@lt@expast#1*#2#3{%
   \@lt@addtopream{#1}%
   \count@#2\relax
   \ifnum\count@>\z@
      \let\@tempa\@empty
      \@whilenum\count@>\z@\do{%
         \@lt@addtopream{#3}%
         \advance\count@\m@ne}%
      \expandafter\@lt@expast
   \else
      \expandafter\remove@to@nnil
   \fi}
\def\@lt@addtopream#1{%
   \expandafter\def\expandafter\@preamble\expandafter{\@preamble#1}}
\newif\if@lt@addcolsep
\def\@lt@mkpream{%
   \let\@preamble\@empty
   \let\@sharp\relax
   \let\@lt@start@entrybox\relax
   \let\@lt@end@entrybox\relax
   \let\@lt@start@pbox\relax
   \let\@lt@end@pbox\relax
   \let\@lt@putoption\relax
   \@chclass\m@ne
   \@firstamptrue
   \@lt@addcolseptrue
   \@tempcntb\z@
   \@lt@mkpream@loop}
\def\@lt@mkpream@loop#1{%
   \ifx#1\@nnil
      \let\@tempa\relax
   \else
      \@lastchclass\@chclass
      \def\@tempa{\@lt@addentry}%
      \if     #1l\relax
         \@chclass\z@
         \@tempcnta\@ne
      \else\if#1c\relax
         \@chclass\z@
         \@tempcnta\z@
      \else\if#1r\relax
         \@chclass\z@
         \@tempcnta\m@ne
      \else\if#1p\relax
         \@chclass\z@
         \def\@tempa{\@lt@addparbox}%
      \else\if#1|\relax
         \@chclass\@ne
         \def\@tempa{\@lt@addvrule}%
      \else\if#1@\relax
         \@chclass\tw@
         \def\@tempa{\@lt@readopt}%
      \else
         \def\@tempa{\@lt@mkpream@loop}%
      \fi\fi\fi\fi\fi\fi
   \fi
   \@tempa}
\def\@lt@addentry{%
   \edef\@tempa{%
      \ifnum\@tempcnta>\z@\else \hfil \fi
      \@lt@start@entrybox\ignorespaces\@sharp\unskip\@lt@end@entrybox
      \ifnum\@tempcnta<\z@\else \hfil \fi}%
   \ifnum\@lastchclass=\z@ \@lt@addcolsep \fi
   \if@firstamp \@firstampfalse \else \@lt@addtopream{&}\fi
   \@lt@addcolsep
   \@csc@t\@preamble\@preamble\@tempa
   \@lt@addcolseptrue
   \advance\@tempcntb\@ne
   \@lt@mkpream@loop}
\def\@lt@addparbox#1{%
   \edef\@tempa{\@lt@start@pbox{#1}\ignorespaces\@sharp\unskip\@lt@end@pbox}%
   \ifnum\@lastchclass=\z@ \@lt@addcolsep \fi
   \if@firstamp \@firstampfalse \else \@lt@addtopream{&}\fi
   \@lt@addcolsep
   \@csc@t\@preamble\@preamble\@tempa
   \@lt@addcolseptrue
   \advance\@tempcntb\@ne
   \@lt@mkpream@loop}
\def\@lt@addvrule{\@ifnextchar[\@lt@addvrule@{\@lt@addvrule@[\arrayrulewidth]}}
\def\@lt@addvrule@[#1]{%
   \dimen@#1\relax
   \edef\@tempa{\vrule width\the\dimen@\relax}%
   \ifcase\@lastchclass
      \@lt@addcolsep
   \or
      \@lt@addtopream{\hskip\@lt@doublerulesep}%
   \else
      \relax
   \fi
   \@csc@t\@preamble\@preamble\@tempa
   \@lt@mkpream@loop}
\def\@lt@readopt#1{%
   \@lt@addcolsepfalse
   \@lt@addtopream{\@lt@putoption{#1}}%
   \@lt@mkpream@loop}
\def\@lt@addcolsep{\if@lt@addcolsep \@lt@addtopream{\hskip\tabcolsep}\fi}
\def\@lt@init{%
   \global\@lt@maxcols\@tempcntb
   \@whilenum\@tempcntb>\z@\do{%
      \@ifundefined{@lt@wd@\the\@lt@id @\the\@tempcntb}{%
         \@namedef{@lt@wd@\the\@lt@id @\the\@tempcntb}{\z@}}{}%
      \global\@namedef{@lt@maxwd@\the\@tempcntb}{\z@}%
      \advance\@tempcntb\m@ne}%
   \gdef\@lt@maxht{\z@}%
   \gdef\@lt@maxdp{\z@}%
   \let\@lt@firstline\@empty
   \count@\z@
   \@whilenum\count@<\@lt@maxcols\do{%
      \advance\count@\@ne
      \edef\@tempa{%
         \ifnum\count@>\@ne &\fi
         \vrule \@width\@nameuse{@lt@wd@\the\@lt@id @\the\count@}%
                \@height\z@ \@depth\z@}%
      \edef\@lt@firstline{\@lt@firstline\@tempa}}%
   \def\@tempa{\tabskip\z@skip}%
   \@csc@t\@preamble\@tempa\@preamble
   \edef\@lt@firstline{%
      &########\tabskip\@centering\cr
       \global\noexpand\@lt@wdcheckfalse
       \@lt@firstline
      &\global\@lt@colcnt\z@
       \global\noexpand\@lt@wdchecktrue\cr}%
   \@csc@t\@preamble\@preamble\@lt@firstline
   \baselineskip\z@skip
   \lineskip\z@skip
   \lineskiplimit\maxdimen
   \setbox\@arstrutbox\hbox{%
      \vrule \@height\arraystretch\ht\strutbox
             \@depth\arraystretch \dp\strutbox
             \@width\z@}%
   \setbox\@lt@head\box\voidb@x
   \setbox\@lt@firsthead\box\voidb@x
   \setbox\@lt@foot\box\voidb@x
   \setbox\@lt@lastfoot\box\voidb@x
   \global\setbox\@lt@prevline\box\voidb@x
   \global\@lt@colcnt\z@
   \let\par\@empty
   \let\@sharp##%
   \let\@lt@start@entrybox\@lt@start@entrybox@
   \let\@lt@end@entrybox\@lt@end@entrybox@
   \let\@lt@start@pbox\@lt@start@pbox@
   \let\@lt@end@pbox\@lt@end@pbox@
   \let\@lt@putoption\@lt@putoption@
   \def\@lt@headbox{%
      \ifvoid\@lt@firsthead \@lt@head
      \else                 \@lt@firsthead \fi}%
   \let\\\@lt@cr
   \let\cline\@lt@cline
   \let\hline\@lt@hline
   \let\multicolumn\@lt@multicolumn
   \let\caption\@lt@setcaption
   \let\@@label\label
   \let\label\@lt@label
   \let\newpage\tabularbreak
   \global\@lt@nocaptiontrue
   \global\let\@lt@makecaption@stepcounter\@lt@makecaption@stepcounter@
   \global\let\@lt@caption\@empty
   \global\let\@lt@captionnumber\@empty
   \gdef\@lt@optional@vspace{\z@}}
\def\@lt@start@entrybox@{\setbox\z@\hbox\bgroup}
\newif\if@lt@wdcheck
\global\@lt@wdchecktrue
\def\@lt@end@entrybox@{\@lt@end@entrybox@@\@ne}
\def\@lt@end@entrybox@@#1{%
   \egroup
   \ifdim\@lt@maxht<\ht\z@ \xdef\@lt@maxht{\the\ht\z@}\fi
   \ifdim\@lt@maxdp<\dp\z@ \xdef\@lt@maxdp{\the\dp\z@}\fi
   \count@#1\relax \ifnum\count@<\@ne \count@\@ne \fi
   \dimen@\wd\z@ \divide\dimen@\count@
   \if@lt@wdcheck
      \@whilenum\count@>\z@\do{%
         \global\advance\@lt@colcnt\@ne
         \advance\count@\m@ne
         \ifdim\csname @lt@maxwd@\the\@lt@colcnt\endcsname<\dimen@
            \expandafter\xdef\csname @lt@maxwd@\the\@lt@colcnt\endcsname{%
               \the\dimen@}%
         \fi}%
   \fi
   \unhbox\z@}
\def\@lt@start@pbox@#1{\setbox\z@\hbox\bgroup
   \vtop\bgroup\hsize#1\relax\@arrayparboxrestore}
\def\@lt@end@pbox@{%
   \if@lt@wdcheck \@finalstrut\@arstrutbox\par \fi
   \egroup\@lt@end@entrybox@@\@ne}
\def\@lt@putoption@{%
   \if@lt@wdcheck \expandafter\@firstofone
   \else          \expandafter\hphantom    \fi}
\def\@lt@cr{%
   &%%% terminate the entry in the last column
   {\ifnum0=`}\fi
   \@ifstar\@lt@cr@\@lt@cr@}
\def\@lt@cr@{\@ifnextchar[\@lt@cr@@{\@lt@cr@@[\z@]}}
\def\@lt@cr@@[#1]{%
   \ifdim#1<\z@ \expandafter\@lt@ncr
   \else        \expandafter\@lt@pcr \fi
   {#1}}
\def\@lt@pcr#1{\ifnum0=`{\fi}%
   \gdef\@lt@optional@vspace{\z@}%
   \@tempdima\ht\@arstrutbox
   \@tempdimb\dp\@arstrutbox \advance\@tempdimb#1\relax
   \vrule\@height\@tempdima \@depth\@tempdimb \@width\z@
   \dimen@
      \ifdim\@lt@maxht<\@tempdima \@tempdima
      \else                       \@lt@maxht \fi
   \advance\dimen@
      \ifdim\@lt@maxdp<\@tempdimb \@tempdimb
      \else                       \@lt@maxdp \fi
   \@tempdima\@lt@goalsize \advance\@tempdima-\dimen@
   \ifdim\@tempdima<\z@
      \gdef\@lt@next{\@lt@breaktabular}%
   \else
      \global\@lt@goalsize\@tempdima
      \global\let\@lt@next\@empty
   \fi
   \global\@lt@colcnt\z@
   \gdef\@lt@maxht{\z@}%
   \gdef\@lt@maxdp{\z@}%
   \cr
   \@lt@next}
\def\@lt@ncr#1{\ifnum0=`{\fi}%
   \xdef\@lt@optional@vspace{#1}%
   \copy\@arstrutbox
   \dimen@
      \ifdim\@lt@maxht<\ht\@arstrutbox \ht\@arstrutbox
      \else                            \@lt@maxht     \fi
   \advance\dimen@
      \ifdim\@lt@maxdp<\dp\@arstrutbox \dp\@arstrutbox
      \else                            \@lt@maxdp     \fi
   \@tempdima\@lt@goalsize \advance\@tempdima-\dimen@
   \ifdim\@tempdima<\z@
      \gdef\@lt@next{\@lt@breaktabular}%
   \else
      \@tempdimb\@lt@optional@vspace\relax
      \advance\@tempdima-\@tempdimb
      \global\@lt@goalsize\@tempdima
      \gdef\@lt@next{\noalign{\vskip\@lt@optional@vspace}}%
   \fi
   \global\@lt@colcnt\z@
   \gdef\@lt@maxht{\z@}%
   \gdef\@lt@maxdp{\z@}%
   \cr
   \@lt@next}
\newdimen\@@arrayrulewidth
\global\@@arrayrulewidth\arrayrulewidth
\global\@@arrayrulewidth\arrayrulewidth
\def\@lt@hline{%
   \noalign{\ifnum0=`}\fi
   \@ifnextchar[\@lt@hline@{\@lt@hline@[\arrayrulewidth]}}
\def\@lt@hline@[#1]{%
   \dimen@#1\relax \ifdim\dimen@<\z@ \dimen@\z@ \fi
   \global\@@arrayrulewidth\dimen@
   \hrule height\z@
   \global\advance\@lt@goalsize-\dimen@
   \@ifnextchar[\@lt@hline@@\@lt@hline@@}%%% skip redundant spaces
\def\@lt@hline@@{\futurelet\@tempa\@lt@hline@@@}
\def\@lt@hline@@@{%
   \ifx\@tempa\hline
      \global\advance\@lt@goalsize-\@lt@doublerulesep
   \fi
   \xdef\@lt@gtempa{%
      \noexpand\@@cline@{1}{\the\@lt@maxcols}%
      \noalign{%
         \ifx\@tempa\hline \vskip\@lt@doublerulesep \fi
         \global\@@arrayrulewidth\arrayrulewidth}}%
   \ifnum0=`{\fi}%
   \@lt@gtempa}
\def\@lt@cline{%
   \noalign{\ifnum0=`}\fi
   \@ifnextchar[\@lt@cline@{\@lt@cline@[\arrayrulewidth]}}
\def\@lt@cline@[#1]{%
   \global\@@arrayrulewidth#1\relax
   \ifnum0=`{\fi}%
   \@lt@cline@@}
\def\@lt@cline@@#1{\@cline#1\@nil}
\def\@cline#1-#2\@nil{%
   \@@cline@{#1}{#2}%
   \noalign{%
      \vskip-\@@arrayrulewidth
      \global\@@arrayrulewidth\arrayrulewidth}}
\def\@@cline@#1#2{%
   \omit
   \@multicnt#1%
   \advance\@multispan\m@ne
   \ifnum\@multicnt=\@ne\@firstofone{&\omit}\fi
   \@multicnt#2%
   \advance\@multicnt-#1%
   \advance\@multispan\@ne
   \leaders\hrule\@height\@@arrayrulewidth\hfill
   \cr}
\def\@lt@starttabular{\@tempdimb\z@\@lt@starttabular@}
\def\@lt@starttabular@{%
   \@set@captionskip@for@table
   \ifx\@lt@caption\@empty
      \setbox\@lt@captionbox\box\voidb@x
   \else
      \if@lt@usecaption
         \setbox\@lt@captionbox\vbox{%
            \hsize\@lt@caption@hsize \linewidth\hsize
            \@lt@makecaption\@lt@caption}%
      \else
         \setbox\@lt@captionbox\box\voidb@x
      \fi
   \fi
   \dimen@\z@
   \@for\@tempa:=\@lt@captionbox,\@lt@headbox,\@lt@foot\do{%
      \advance\dimen@\ht\@tempa\relax
      \advance\dimen@\dp\@tempa\relax}%
   \@tempdima\textheight \advance\@tempdima-\dimen@
   \advance\@tempdima-\@tempdimb
   \global\@lt@goalsize\@tempdima
   \global\@lt@colcnt\z@
   \gdef\@lt@maxht{\z@}%
   \gdef\@lt@maxdp{\z@}%
   \setbox\@lt@currbox\vbox\bgroup
      \hsize\@lt@hsize \tabskip\@centering
      \def\@tempa{\halign to\@lt@hsize}%
      \expandafter\@tempa\expandafter\bgroup\@lt@preamble}
\def\@lt@endtabular#1{%
   \crcr\egroup\egroup
   \ifx#1\@empty\relax \else
      \setbox#1\box\@lt@currbox
      \expandafter\@lt@starttabular
   \fi}
\def\endhead{\@lt@endtabular\@lt@head}
\def\endfirsthead{\@lt@endtabular\@lt@firsthead}
\def\endfoot{\@lt@endtabular\@lt@foot}
\def\endlastfoot{\@lt@endtabular\@lt@lastfoot}
\def\@lt@setcaption{%
   \noalign{\ifnum0=`}\fi
   \@ifstar\@lt@setcaption@\@lt@setcaption@}
\def\@lt@setcaption@{\@ifnextchar[\@lt@setcaption@@{\@lt@setcaption@@[]}}
\long\def\@lt@setcaption@@[#1]#2{%
   \global\@lt@nocaptionfalse
   \gdef\@lt@captionnumber{#1}%
   \gdef\@lt@caption{#2}%
   \@lt@remove@cr}
\def\@lt@remove@cr{\@ifnextchar[\@lt@remove@cr@\@lt@remove@cr@}
\def\@lt@remove@cr@{\futurelet\let@token\@lt@remove@cr@@}
\def\@lt@remove@cr@@{%
   \ifx\let@token\\%
      \def\@tempa{\@gobble}%
   \else
      \let\@tempa\@empty
   \fi
   \ifnum0=`{\fi\expandafter}\@tempa}
\def\@lt@label#1{%
   \noalign{\ifnum0=`}\fi
   \def\@tempa{#1}%
   \@onelevel@sanitize\@tempa
   \edef\@tempa{\noexpand\label{\@tempa}}%
   \@csc@t\@tempa\@lt@caption\@tempa
   \global\let\@lt@caption\@tempa
   \@lt@remove@cr}
\def\@lt@makecaption{%
   \@lt@makecaption@stepcounter
   \global\let\@lt@makecaption@stepcounter\relax
   \@dblarg\@lt@makecaption@}
\def\@lt@makecaption@stepcounter@{%
   \ifx\@lt@captionnumber\@empty
      \refstepcounter{table}%
      \global\let\@lt@currentlabel\@currentlabel
      \gdef\@lt@currnumber{\fnum@table}%
   \else
      \global\let\@lt@currentlabel\@lt@captionnumber
      \gdef\@lt@currnumber{\tablename~\@lt@captionnumber}%
   \fi}%
\global\let\@lt@currentlabel\@empty
\long\def\@lt@makecaption@[#1]#2{%
   \par
   \begingroup
   \@parboxrestore
   \if@minipage \@setminipage \fi
   \let\label\@@label
   \let\@currentlabel\@lt@currentlabel
   \normalsize
   \@makecaption\@lt@currnumber{\ignorespaces #2}\par
   \endgroup}
\def\@lt@breaktabular{%
   \egroup\egroup
   \setbox\@lt@currbox\vbox{%
      \unvbox\@lt@currbox
      \global\setbox\@ne\lastbox}%
   \@lt@output@tabular\voidb@x
   \global\setbox\@lt@prevline\box\@ne
   \@tempdimb\ht\@lt@prevline \advance\@tempdimb\dp\@lt@prevline
   \@lt@starttabular@}
\def\tabularbreak{%
   \egroup\egroup
   \@lt@output@tabular\voidb@x
   \global\setbox\@lt@prevline\box\voidb@x
   \@tempdimb\z@
   \@lt@starttabular@}
\def\@lt@output@tabular#1{%
   \ifnum#1<\z@\else
      \setbox\@lt@currbox\vbox{%
         \box\@lt@captionbox
         \copy\@lt@headbox
         \box\@lt@prevline
         \vskip\@lt@optional@vspace
         \box\@lt@currbox
         \def\@tempa{\@lt@foot}%
         \ifnum#1=\@lt@lastfoot \ifvoid\@lt@lastfoot\else
            \def\@tempa{\@lt@lastfoot}%
         \fi\fi
         \copy\@tempa}%
   \fi
   \def\@lt@headbox{\@lt@head}%
   \@lt@output@tabular@}
\def\@lt@output@tabular@{%
   \ifx\@lt@firstposition\@empty
      \def\@tempa{\relax}%
   \else
      \edef\@tempa{[\@lt@firstposition]}%
      \let\@lt@firstposition\@empty
   \fi
   \edef\@tempa{\noexpand\@dblfloat{table}\@tempa}%
   \@tempa\box\@lt@currbox\end@dblfloat
   \if@lt@usecaption \gdef\@lt@caption{(Continued)}\fi} %%%08D14
\def\@lt@write@boxsize{%
   \if@filesw
      \count@\z@
      \@tempswafalse
      \@whilenum\count@<\@lt@maxcols\do{%
         \advance\count@\@ne
         \@tempdima\csname @lt@maxwd@\the\count@\endcsname\relax
         \@tempdimb\csname @lt@wd@\the\@lt@id @\the\count@\endcsname\relax
         \advance\@tempdima-\@tempdimb
         \ifdim\@tempdima<\z@ \@tempdima-\@tempdima \fi
         \ifdim\@lt@colwd@fuzz<\@tempdima \@tempswatrue \fi
         \immediate\write\@auxout{%
            \string\@set@ltdata{\the\@lt@id}{\the\count@}{%
               \csname @lt@maxwd@\the\count@\endcsname}}}%
   \else
      \@tempswafalse
   \fi
   \if@tempswa
      \@lt@warning{The width of each column may have changed.}%
   \fi}
\def\@lt@colwd@fuzz{.1\p@}
\def\@set@ltdata#1#2#3{\expandafter\gdef\csname @lt@wd@#1@#2\endcsname{#3}}
\long\def\@lt@multicolumn#1#2#3{%
   \multispan{#1}\begingroup
   \let\@preamble\@empty
   \protected@edef\@tempa{#2}%
   \expandafter\@lt@expast\@tempa*0x\@nnil
   \expandafter\@lt@mkpream\@preamble\@nnil
   \def\@sharp{#3}\set@typeset@protect
   \let\@lt@start@entrybox\@lt@start@entrybox@
   \def\@lt@end@entrybox{\@lt@end@entrybox@@{#1}}%
   \let\@lt@start@pbox\@lt@start@pbox@
   \def\@lt@end@pbox{%
      \@finalstrut\@arstrutbox\par\egroup\@lt@end@entrybox@@{#1}}%
   \let\@lt@putoption\@lt@putoption@
   \@arstrut\@preamble\hbox{}\endgroup\ignorespaces}
%
%%% make a slight change to array/tabular environment
\def\@array[#1]#2{%
   \if #1t\vtop \else \if#1b\vbox \else \vcenter \fi\fi
   \bgroup
   \setbox\@arstrutbox\hbox{%
      \vrule \@height\arraystretch\ht\strutbox
             \@depth\arraystretch \dp\strutbox
             \@width\z@}%
   \@mkpream{#2}%
   \edef\@preamble{%
      \ialign \noexpand\@halignto
         \bgroup \@arstrut \@preamble \tabskip\z@skip \cr}%
   \let\@startpbox\@@startpbox \let\@endpbox\@@endpbox
   \let\tabularnewline\\%
   \let\par\@empty
   \let\multicolumn\@@multicolumn
   \let\cline\@@cline
   \let\hline\@@hline
   \let\@sharp##%
   \set@typeset@protect
   \lineskip\z@skip\baselineskip\z@skip
   \ifhmode \@preamerr\z@ \@@par\fi
   \@preamble}
\let\@@cline\cline
\let\@@hline\hline
\let\@@multicolumn\multicolumn
%
%%% page styles
\let\lett\@empty
\def\ps@myheadings{%
   \let\@oddfoot\@empty\let\@evenfoot\@empty
   \def\@evenhead{%
      \@set@proofmark
      \thepage\hfil\slshape\leftmark}%
   \def\@oddhead{%
      \@set@proofmark
      {\slshape\rightmark}\hfil\thepage}%
   \let\@mkboth\@gobbletwo}
\def\@sidelabelsep{13pt}
\def\ps@firstpage{%
   \def\@oddhead{\hbox to \textwidth{\vbox to 54pt{\hsize250pt{\rhfont{\itshape Publications of the Astronomical Society of Japan},\ \@jyear,\ \textbf{\@jvol},\ \thepage--\@endpage\par%
\@doi\par Advance access publication date:\ \pdate\par}\vfill}\hfill\raise9pt\hbox{\fboxsep=0pt\fbox{\vbox to 45pt{\hbox to 37pt{}}}\hspace*{1pc}\fbox{\vbox to 45pt{\hbox to 37pt{}}}}}}%
   \let\@evenhead\@oddhead
   \def\@oddfoot{\hbox to \textwidth{%
     \vbox to -25pt{{\hsize\textwidth\rule{\textwidth}{.5pt}\par\vspace*{1pt}%
{\historyfont%
\textbf{Received:}\ \@make@formatted@date\rdate
 , \textbf{Accepted:}\ \@make@formatted@date\adate\hfill}%
 {\rffont\copyright\ \@jyear.\ Astronomical Society of Japan.\par}}}}}%
   \def\@evenfoot{}%
   \let\@mkboth\@gobbletwo}
%%
\def\oddfolio{{\foliofont\thepage}}
\def\evenfolio{{\foliofont\thepage}}
%%
\def\ps@headings{%
   \def\@evenhead{\vbox{\hsize\textwidth%
{\evenfolio}\hfill{\rhhfont{\itshape Publications of the Astronomical Society of Japan}\ (\@jyear),\ Vol.\ \@jvol,\ No.\ \@Issue}}}%
   \def\@oddhead{\vbox{\hsize\textwidth%
{\rhhfont{\itshape Publications of the Astronomical Society of Japan}\ (\@jyear),\ Vol.\ \@jvol,\ No.\ \@Issue}\hfill{\oddfolio}}}%%%
   \def\@oddfoot{%
      \hfill
      \rlap{%
         \kern\@sidelabelsep
         \@put@sidelabel\@oddsidelabel}}%
   \def\@evenfoot{%
      \llap{%
         \@put@sidelabel\@evensidelabel
         \kern\@sidelabelsep}%
      \hfill}%
   \let\@mkboth\@gobbletwo}
\def\@put@sidelabel#1{%
   \vbox to\z@{\hsize\evensidemargin
      \vss
      \vbox to\textheight{\vss#1}%
      \vskip\footskip}}
\let\@oddsidelabel\@empty
\let\@evensidelabel\@empty
\def\@@Author{\ifx\@Author\relax \leftmark \else \@Author \fi}
\def\@@runninghead{\ifx\@runninghead\relax \rightmark \else \@runninghead \fi}
\def\ps@headnombre{%
   \def\@oddhead{%
      \@set@proofmark
      \hfill{\slshape\thepage}}%
   \def\@evenhead{%
      \@set@proofmark
      {\slshape\thepage}\hfill}%
   \let\@oddfoot\@empty
   \let\@evenfoot\@empty
   \let\@mkboth\@gobbletwo}
\def\ps@sample{%
   \let\ps@firstpage\ps@plain
   \def\@evenhead{\normalsize\normalfont
      \rlap{\lett\thepage}\hfill\@@Author\hfill}%
   \def\@oddhead{\normalsize\normalfont
      \hfill\@@runninghead\hfill\llap{\lett\thepage}}%
   \let\@oddfoot\@empty
   \let\@evenfoot\@empty
   \let\@mkboth\@gobbletwo}
\let\@set@proofmark\relax
%
%%% bibliography
\def\etal{et~al.}
\newdimen\bibindent
\setlength\bibindent{1.5em}
\def\newblock{\hskip .11em\@plus.33em\@minus.07em}
\let\@openbib@code\@empty
%%%\let\@biblabel\@firstofone
\let\ADSentry\@secondoftwo
\def\bibsectionfont{\fontfamily{\sfdefault}\if@proofread\fontsize{12}{14}\else\fontsize{11}{11}\fi\selectfont\bfseries\rightskip0pt plus1fill}
%%
\def\thebibliography#1{\let\sectionfont\bibsectionfont%
   \if@twocolumn
      \let\@tempa\relax
   \else
      \if@noskipsec \leavevmode \fi
      \ifhmode \unskip\par \fi
      \addvspace\defaultbaselineskip
      \nobreak
      \if@proofread \let\@tempa\relax
      \else         \def\@tempa{\@init@twocolbib}%
      \fi
   \fi
   \@tempa
   \global\@in@appendixfalse
   \bibliofont%
   \section*{\bibname}%
   \list{}%
      {\leftmargin 12pt
       \itemindent-\leftmargin
       \labelwidth\z@
       \itemsep\z@}%
   \let\@prev@author\@empty
   \let\@bib@year\@empty
   \sloppy \sfcode`\.=\@m \hyphenpenalty\@M
   \bibliofont}
\def\endthebibliography{%
   \def\@noitemerr{\@latex@warning{Empty `thebibliography' environment}}%
   \@topsepadd\z@
   \endlist
   \let\@tempa\relax
   \if@twocolumn\else \if@proofread\else
      \def\@tempa{\@close@twocolbib}%
   \fi\fi
   \@tempa}
\def\bibitem{\@ifnextchar[\@lbibitem\@bibitem}
\def\@bibitem{%
   \let\@bib@author\@prev@author
   \@set@biblabel}
\def\@lbibitem[#1]{%
   \@bib@parse#1()\@nil
   \@set@biblabel}
\def\@bib@parse#1(#2)#3\@nil{%
   \def\@bib@author{#1}%
   \protected@edef\@bib@year{\zap@space#2 \@empty}}
\def\@set@biblabel#1{%
   \ifx\@bib@author\@empty
      \@latex@warning{Author name should be given
         for reference entry ``#1''}%
   \fi
   \ifx\@bib@year\@empty
      \@latex@warning{Publication year should be given
         for reference entry ``#1''}%
   \fi
   \if@filesw
      \begingroup
      \let\protect\noexpand
      \immediate\write\@auxout{%
         \string\bibcite{\@ref@prefix#1}{{\@bib@author}{\@bib@year}}}%
      \endgroup
   \fi
   \let\@prev@author\@bib@author
   \item[]}
\def\bysame{\ifvmode\leavevmode\fi \hbox to3em{\hrulefill}\thinspace}
\newbox\@bib@textbox
\def\textminimum{3}
\def\@init@twocolbib{%
   \dimen@\textwidth \advance\dimen@-\columnsep \divide\dimen@\tw@
   \columnwidth\dimen@
   \global\setbox\@bib@textbox\vbox\bgroup
      \hsize\dimen@
      \@parboxrestore
      \@setminipage}
\def\@close@twocolbib{%
      \ifhmode \unskip\par \fi
      \vskip-\lastskip
      \global\@minipagefalse
      \egroup
   \@twocolbib@sizecheck}
\def\@twocolbib@sizecheck{%
   \ifdim\pagegoal>\textheight
      \dimen@\@colroom
   \else
      \dimen@\pagegoal \advance\dimen@-\pagetotal
   \fi
   \@tempdima\defaultbaselineskip\relax \@tempdima\textminimum\@tempdima
   \ifdim\dimen@<\@tempdima
      \ifdim\dimen@>\z@
         \def\@tempa{\vbox{}\newpage\@twocolbib@sizecheck}%
      \else
         \def\@tempa{\vbox{}\@twocolbib@sizecheck}%
      \fi
   \else
      \def\@tempa{\@twocolbib@splitbox}%
   \fi
   \@tempa}
\def\@twocolbib@htfuzz{\p@}
\def\@twocolbib@splitbox{%
   \begingroup
   \vbadness\@M \vfuzz\maxdimen
   \ifdim.5\ht\@bib@textbox<\dimen@
      \dimen\tw@\defaultbaselineskip\relax
      \@tempdima.5\ht\@bib@textbox
      \dimen@\@tempdima
      \@tempdimb\maxdimen
      \setbox4\box\@bib@textbox
      \@whiledim\@tempdima<\@tempdimb\do{%
         \setbox6=\copy4\relax
         \setbox\z@\vsplit6 to\dimen@
         \setbox\z@\vbox{\unvbox\z@\vskip-\lastskip}%
         \setbox\tw@\vbox{\unvbox6\vskip-\lastskip}%
         \@tempdima\ht\z@  \advance\@tempdima\dp\z@
         \@tempdimb\ht\tw@ \advance\@tempdimb\dp\tw@
         \advance\@tempdima\@twocolbib@htfuzz\relax
         \advance\dimen@.5\dimen\tw@}%
   \else
      \setbox\z@ \vsplit\@bib@textbox to\dimen@
      \setbox\z@\vbox{\unvbox\z@}%
      \setbox\tw@\vsplit\@bib@textbox to\dimen@
      \setbox\tw@\vbox{\unvbox\tw@}%
   \fi
   \@tempdima\ht\z@
   \@tempdimb\ht\tw@
   \dimen@ \ifdim\@tempdima>\@tempdimb \@tempdima \else \@tempdimb \fi
   \@tempdima \ifdim\dp\z@<\dp\tw@ \dp\tw@ \else \dp\z@ \fi
   \hbox to\textwidth{%
      \hbox to\columnwidth{%
         \vbox to\dimen@{\unvbox\z@\vfill\hrule\@height\z@}%
         \hss}%
      \hss
      \hbox to\columnwidth{%
         \vbox to\dimen@{\unvbox\tw@\vfill\hrule\@height\z@}%
         \hss}}%
   \endgroup
   \ifvoid\@bib@textbox \let\@tempa\@empty
   \else                \def\@tempa{\newpage\@twocolbib@sizecheck}%
   \fi
   \@tempa}
\DeclareRobustCommand\cite{\@cite@\@empty\@empty\@citeform@both}
\DeclareRobustCommand\yearcite{\@cite@\@empty\@empty\@citeform@year}
\DeclareRobustCommand\authorcite{\@cite@\@empty\@empty\@citeform@author}
\DeclareRobustCommand\citep{\@cite@()\@citeform@both}
\DeclareRobustCommand\citet{\@cite@\@empty\@empty\@citeform@text}
\def\@cite@#1#2#3{%
   \def\@cite@prefix{#1}%
   \def\@cite@suffix{#2}%
   \@ifnextchar[%
      {\@tempswatrue\let\@citeform#3\@citex}%
      {\@tempswafalse\let\@citeform#3\@citex[]}}
\def\@citex[#1]#2{%
   \let\@citea\@empty
   \@cite{\@for\@citeb:=#2\do{%
      \@citea\def\@citea{;\penalty\@m\ }%
      \edef\@citeb{\expandafter\@firstofone\@citeb\@empty}%
      \if@filesw\immediate\write\@auxout{\string\citation{\@citeb}}\fi
      \@ifundefined{b@\@ref@prefix\@citeb}%
         {\mbox{\reset@font\bfseries ?}%
          \G@refundefinedtrue
         \@latex@warning{Citation `\@citeb' on page \thepage\space undefined}}%
         {\@citeform\@citeb}}}{#1}}
\def\@citeform@both#1{%
   \expandafter\expandafter\expandafter\@citeform@both@
   \csname b@\@ref@prefix#1\endcsname\@empty\@empty}
\def\@citeform@both@#1#2{#1\penalty0\ #2}
\def\@citeform@year#1{%
   \expandafter\expandafter\expandafter\@secondoftwo
   \csname b@\@ref@prefix#1\endcsname\@empty\@empty}
\def\@citeform@author#1{%
   \expandafter\expandafter\expandafter\@firstoftwo
   \csname b@\@ref@prefix#1\endcsname\@empty\@empty}
\def\@citeform@text#1{%
   \expandafter\expandafter\expandafter\@firstoftwo
   \csname b@\@ref@prefix#1\endcsname\@empty\@empty
   \penalty0\ (%
   \expandafter\expandafter\expandafter\@secondoftwo
   \csname b@\@ref@prefix#1\endcsname\@empty\@empty)}
\def\nocite#1{\@bsphack
   \@for\@citeb:=#1\do{%
      \edef\@citeb{\expandafter\@firstofone\@citeb}%
      \if@filesw\immediate\write\@auxout{\string\citation{\@citeb}}\fi
      \@ifundefined{b@\@ref@prefix\@citeb}%
         {\G@refundefinedtrue
          \@latex@warning{Citation `\@citeb' undefined}}{}}%
   \@esphack}
\def\@cite#1#2{{\@cite@prefix#1\if@tempswa , #2\fi\@cite@suffix}}
\let\@cite@prefix\@empty
\let\@cite@suffix\@empty
\def\article{\@ifnextchar[\@article{\@article[]}}
\def\@article[#1]#2{%
   \IfFileExists{#2}%
      {\begingroup
       \global\advance\@articleid\@ne
       \if@filesw
          \immediate\write\@auxout{%
             \string\@articledata{#2}%
                {{\the\@articleid}{\the\@lt@id}{\the\c@page}}}%
       \else
          \expandafter\ifx\csname @articledata@for@#2\endcsname\relax\else
             \expandafter\expandafter\expandafter\@split@articledata
                \csname @articledata@for@#2\endcsname\@empty\@empty\@empty
          \fi
       \fi
       \begingroup
       \let\@elt\@stpelt
       \cl@@article
       \endgroup
       \@aftersectionfalse
       \let\label\@article@label
       \let\ltx@label\@article@label%%% for amsmath package
       \let\ref\@article@ref
       \edef\@ref@prefix{\the\@articleid:}%
       \let\pageref\@article@pageref
       \let\@Author\relax
       \let\@runninghead\relax
       \let\@keywords\@empty
       \let\@title\@empty
       \let\@author\@empty
       \let\@affil@prefix\@empty
       \let\@affil@break\@empty
       \let\rdate\@empty
       \let\adate\@empty
       \let\pdate\@empty
       \let\@abstract\@empty
       \@skip@abstractfalse
       \let\@thanks\@empty
       \setbox\@abstract@textbox\box\voidb@x
       \let\@post@abstract\relax
       \edef\pageSTART{\thepage}%
       \edef\@tempa{r@\@ref@prefix @article:\the\@articleid:@}%
       \expandafter\ifx\csname\@tempa\endcsname\relax
          \typeout{Warning [pasj]: Last page for article `#2' is unknown.}%
          \def\pageEND{{\bfseries??}}%
          \def\@@pageEND{10000}%
       \else
          \edef\pageEND{%
             \expandafter\expandafter\expandafter
             \@secondoftwo\csname\@tempa\endcsname}%
          \let\@@pageEND\pageEND
       \fi
       \let\@plateno\@empty
       \def\theequation{\@arabic\c@equation}%
       \@in@appendixfalse
       \@@input\@filef@und
       \ifvmode \vskip-\lastskip \fi
       \edef\@tempa{\noexpand\label{@article:\the\@articleid:@}}%
       \@tempa
       #1%
       \if@openright \cleardoublepage \else \clearpage \fi
       \if@twocolumn\else \twocolumn \fi
       \endgroup}%
      {\typeout{No file #2.}}}
\def\@split@articledata#1#2#3{%
   \afterassignment\remove@to@nnil
   \global\@articleid 0#1\relax\@nnil
   \afterassignment\remove@to@nnil
   \global\@lt@id 0#2\relax\@nnil
   \afterassignment\remove@to@nnil
   \global\c@page 0#3\relax\@nnil}
\newcount\@articleid
\global\@articleid\z@
\def\@articledata#1#2{%
   \expandafter\gdef\csname @articledata@for@#1\endcsname{#2}}
\let\@ref@prefix\@empty
\def\@article@ref#1{%
   \expandafter\@setref\csname r@\@ref@prefix#1\endcsname
   \@firstoftwo{#1}}
\def\@article@pageref#1{%
   \expandafter\@setref\csname r@\@ref@prefix#1\endcsname
   \@secondoftwo{#1}}
\def\@article@label#1{%
   \@bsphack
   \protected@write\@auxout{}%
      {\string\newlabel{\@ref@prefix#1}{{\@currentlabel}{\thepage}}}%
   \@esphack}
\def\papers{\@ifnextchar[\@papers{\@papers[\papersname]}}
\def\@papers[#1]{%
   \if@filesw
      \immediate\write\@auxout{\string\@writefile{toc}%
         {\string\contentsline{block}{#1}{}}}%
   \fi
   \let\@oddsidelabel\@empty
   \let\@evensidelabel\@empty
   \let\lett\@empty}
\def\letters{\@ifnextchar[\@letters{\@letters[\lettersname]}}
\def\@letters[#1]{%
   \if@filesw
      \immediate\write\@auxout{\string\@writefile{toc}%
         {\string\contentsline{block}{#1}{}}}%
   \fi
   \def\@oddsidelabel{\Loddsidelabel}%
   \def\@evensidelabel{\Levensidelabel}%
   \def\lett{L}}
\def\Loddsidelabel{%
   \setbox\z@\hbox{%
      {\color[gray]{.8}%
       \dimen@\topmargin \advance\dimen@\headheight
       \advance\dimen@\headsep \advance\dimen@ 1in\relax
       \advance\dimen@.05\paperheight
       \@tempdima1.1\paperheight \advance\@tempdima-\dimen@
       \vrule\@width 10mm \@height\dimen@ \@depth\@tempdima}}%
   \ht\z@\z@ \dp\z@\z@ \wd\z@\z@ \box\z@
   \nointerlineskip
   \hbox{%
      \if@pasj@usefigure
         \kern 5\p@
         \vbox to\z@{%
            \vss\kern-15\p@
            \hbox{\rotatebox{90}{\sffamily
               \@makeoutline{L\,E\,T\,T\,E\,R}}}%
            \vss}%
      \else
         \tiny\sffamily LETTER
      \fi}%
   \vfill}
\let\Levensidelabel\@empty
\def\@makeoutline#1{%
   \mbox{%
      \setbox\z@\hbox{{\color{white}#1}}%
      \setbox\tw@\hbox{{\color{black}#1}}%
      \wd\tw@\z@
      \dimen@.2\p@
      \kern-\dimen@\copy\tw@\@@makeoutline\kern\dimen@
      \@@makeoutline
      \kern\dimen@\copy\tw@\@@makeoutline\kern-\dimen@
      \box\z@}}
\def\@@makeoutline{\raise\dimen@\copy\tw@\lower\dimen@\copy\tw@}
%
%%% \maketitle
\def\maketitle{%
   \def\@tempa{\@maketitle}%
   \ifx\@abstract\@empty
      \if@skip@abstract
         \def\@post@abstract{%
            \ifhmode \unskip\par \fi
            \addvspace\topsep
            \unvbox\@abstract@textbox}%
      \else
         \def\@post@abstract{\@maketitle}%
         \let\@tempa\relax
      \fi
   \else
      \def\@post@abstract{%
         \typeout{Notice: There is a redundant abstract environment.}%
         \setbox\@abstract@textbox\box\voidb@x}%
   \fi
   \@tempa}
\newskip\@saved@topsep
\let\@thanks\@empty
\def\@maketitle{%
   \thispagestyle{firstpage}%
   \begingroup
   \def\thefootnote{\fnsymbol{footnote}}%
   \def\@makefnmark{%
      {\normalfont\mathversion{normal}%
       $\m@th{}^{\@thefnmark}$}}%
   \if@twocolumn
      \@@maketitle
      \ifvoid\z@\else
         \@topnewpage[\box\z@]%
      \fi
   \else
      \newpage
      \@@maketitle
      \box\z@
   \fi
   \@thanks
   \endgroup
   \setcounter{footnote}{0}}
\def\@@maketitle{%
   \@saved@topsep\topsep
   \topsep\z@ \partopsep\z@
   \setbox\z@\vbox{\hsize\textwidth \linewidth\textwidth
\vspace*{25pt}%
\parindent0pt%
\begingroup
{\vrule width\textwidth height1pt depth0pt\par\vspace*{13.6pt}}%
{\titlefont\@title\par\vspace*{7pt}}%
{\authorfont \printauthor\par\vspace*{7pt}}%
{\affilfont\@affil\par\vspace*{3.5pt}}%
{\corfont\@email\par\vspace*{16pt}}%
{\idfont\@orcid\par\vspace*{6pt}}%
\endgroup
      \smallskip
      \if@skip@abstract\else
         \ifx\@abstract\@empty
            \vspace\@saved@topsep
            \unvbox\@abstract@textbox
            \vspace{-\@saved@topsep}%
         \else
              {\abstractheadfont \abstractname\par}%
              \vspace\@saved@topsep
              {\abstractfont\@abstract\par}\strut
              \@@par
              \vspace{-\@saved@topsep}%
         \fi
      \fi
      \ifx\@keywords\@empty\else\vspace*{9pt}%
            {\keywordheadfont Keywords:}~{\keywordfont\@keywords\par}
      \fi%
\par\vspace*{3pt}%
%% {\vrule width34.5pc height2pt depth0pt}
      \par%
      \vspace*{15.5pt}}%
   \dimen@\ht\z@ \advance\dimen@\dp\z@
   \@whiledim\dimen@>\textheight\do{%
      \setbox\tw@\vsplit\z@ to\textheight
      \global\setbox\@outputbox\vbox to\textheight{\unvbox\tw@\vss}%
      \@outputpage
      \ifvoid\z@
         \dimen@\z@
      \else
         \setbox\z@\vbox{\unvbox\z@}%
         \dimen@\ht\z@ \advance\dimen@\dp\z@
      \fi}%
   \ifvoid\z@\else
      \dimen@\ht\z@ \advance\dimen@\dp\z@
      \@tempdima\defaultbaselineskip
      \advance\dimen@.8\@tempdima
      \divide\dimen@\@tempdima \count@\dimen@
      \dimen@\count@\@tempdima
      \setbox\z@\vbox to\dimen@{\box\z@\vss\hrule\@height\z@}%
   \fi}
\def\@gobbled@thanks#1#{\@gobbled@thanks@}
\let\@gobbled@thanks@\@gobble
\def\@make@formatted@date#1{%
   \expandafter\@make@formatted@date@#1///\@nil
   \@tempa}
\def\@make@formatted@date@#1/#2/#3/#4\@nil{%
   \def\@tempa{#1}%
   \def\@tempb{#2}%
   \def\@tempc{#3}%
   \def\@tempd{#4}%
   \global\let\@curr@year\@empty
   \ifx\@tempd\@empty\else
      \begingroup
      \afterassignment\remove@to@nnil
      \@tempcnta 0\@tempa\relax\@nnil
      \ifnum\@tempcnta>\z@\else \@tempcnta\z@ \fi
      \year\@tempcnta
      \xdef\@curr@year{\number\year}%
      \afterassignment\remove@to@nnil
      \@tempcnta 0\@tempb\relax\@nnil
      \ifnum\@tempcnta>\z@\else \@tempcnta\z@ \fi
      \month\@tempcnta
      \afterassignment\remove@to@nnil
      \@tempcnta 0\@tempc\relax\@nnil
      \ifnum\@tempcnta>\z@\else \@tempcnta\z@ \fi
      \day\@tempcnta
      \edef\@tempa{\def\noexpand\@tempa{\today}}%
      \expandafter\endgroup\@tempa
   \fi}
\def\thanks{\@ifnextchar[\@othanks\@nthanks}
\def\@othanks[#1]#2{%
   \footnotemark[\ensuremath{#1}]%
   \protected@xdef\@thanks{%
      \@thanks
      \protect\footnotetext[\ensuremath{#1}]{#2}}}
\def\@nthanks#1{%
   \footnotemark
   \protected@xdef\@thanks{%
      \@thanks
      \protect\footnotetext[\thefootnote]{#1}}}
\let\@post@abstract\relax
\newbox\@abstract@textbox
\def\abstract{%
   \global\setbox\@abstract@textbox\vbox\bgroup\parindent0pt%
      \hsize\textwidth \linewidth\hsize
      \topsep\z@ \partopsep\z@
      {\abstractheadfont\abstractname\par\vspace*{3pt}}%
      \abstractfont}
\def\endabstract{%
      \setbox\z@\hbox{g}%
      \ifhmode
         \unskip\nobreak
         \vrule \@width\z@ \@depth\dp\z@
         \par
      \else
         \dimen@\dp\z@
         \advance\dimen@-\prevdepth
         \ifdim\dimen@>\z@ \kern\dimen@ \fi
      \fi
      \vskip-\lastskip\kern\z@
   \egroup
   \aftergroup\@post@abstract}
\newif\if@skip@abstract
\global\@skip@abstractfalse
\def\noabstract{\@skip@abstracttrue}
\let\@abstract\@empty
\long\def\abst#1{\def\@abstract{#1}}
%
%%% old style font-change commands
\DeclareOldFontCommand{\rm}{\normalfont\rmfamily}{\mathrm}
\DeclareOldFontCommand{\sf}{\normalfont\sffamily}{\mathsf}
\DeclareOldFontCommand{\tt}{\normalfont\ttfamily}{\mathtt}
\DeclareOldFontCommand{\bf}{\normalfont\bfseries}{\mathbf}
\DeclareOldFontCommand{\it}{\normalfont\itshape}{\mathit}
\DeclareOldFontCommand{\sl}{\normalfont\slshape}{\@nomath\sl}
\DeclareOldFontCommand{\sc}{\normalfont\scshape}{\@nomath\sc}
\DeclareRobustCommand*\cal{\@fontswitch\relax\mathcal}
\DeclareRobustCommand*\mit{\@fontswitch\relax\mathnormal}
%
%%% tableofcontents
\def\@tocrmarg{50pt}
\def\@toclmarg{3em}
\def\@tocloffset{0pt}
\def\@tocroverfull{0pt}
\def\@dotsep{2}
\setcounter{tocdepth}{2}
\def\tableofcontents{%
   \if@twocolumn
      \@restonecolfalse\onecolumn
   \else
      \@restonecoltrue
   \fi
   \begingroup
   \normalfont
   \@tableofcontents@setup
   \centerline{\bfseries \contentsname}%
   \@starttoc{toc}%
   \newpage
   \if@openright \cleardoublepage \fi
   \endgroup
   \if@restonecol\else\twocolumn\fi}
\def\@tableofcontents@setup{%
   \leftskip\@tocloffset\relax \advance\leftskip\@toclmarg\relax
   \rightskip\@tocrmarg\relax
   \parfillskip-\rightskip \advance\parfillskip-\@tocroverfull\relax
   \dimen@-\parfillskip \edef\@pnumwidth{\the\dimen@}%
   \tolerance3000 \hyphenpenalty\@M}
\def\l@block#1#2{%
   \ifhmode \unskip\par \fi
   \noindent\kern-\@toclmarg{\bfseries#1}%
   \par}
\def\l@misc#1#2{%
   \ifhmode \unskip\par \fi
   \noindent\kern-\@toclmarg{\bfseries#1}%
   \nobreak\hfill\nobreak
   \setbox\z@\hbox{#2}%
   \ifdim\@pnumwidth>\wd\z@ \hbox to\@pnumwidth{\hss\unhbox\z@}%
   \else                    \box\z@                              \fi
   \par}
\def\l@article#1#2{%
   \@toc@get@articledata#1\relax\relax\relax
   \@toc@split@authorlist%%% \count@ := number of authors
   \@toc@rewrite@authorlist
   \ifhmode \unskip\par \fi
   \begingroup
   \begingroup
   \dimen@\@toclmarg\relax \advance\leftskip-\dimen@
   \noindent
   \@toc@title
   \nobreak
   \hfill\nobreak
   \setbox\z@\hbox{\@toc@prefix#2}%
   \ifdim\@pnumwidth>\wd\z@ \hbox to\@pnumwidth{\hss\unhbox\z@}%
   \else                    \box\z@                              \fi
   \par\nobreak
   \endgroup
   \@toc@addbreakfalse
   \parfillskip\z@\@plus 1fil
   \noindent
   {\itshape\@toc@authors}%
   \par\endgroup
   \addvspace{.5\defaultbaselineskip}}
\def\@toc@get@articledata#1#2#3{%
   \def\@toc@authorlist{#1}%
   \def\@toc@title{#2}%
   \def\@toc@prefix{#3}}
\def\@toc@split@authorlist{%
   \let\@toc@templist\@empty
   \count@\z@
   \expandafter\@toc@split@authorlist@\@toc@authorlist\@nil}
\def\@toc@split@authorlist@{%
   \@ifnextchar\bgroup
      \@toc@split@authorlist@loop
      \@toc@split@authorlist@@}
\def\@cs@break{\break}
\def\@toc@split@authorlist@loop#1{%
   \def\@toc@tempa{#1}%
   \ifx\@toc@tempa\@nnil
      \let\@toc@authorlist\@toc@templist
   \else
      \ifx\@toc@tempa\@cs@break\else \advance\count@\@ne \fi
      \def\@toc@tempa{\@toc@elt{#1}}%
      \@csc@t\@toc@templist\@toc@templist\@toc@tempa
      \expandafter\@toc@split@authorlist@loop
   \fi}
\def\@toc@split@authorlist@@#1\@nil{%
   \count@\@ne
   \def\@toc@authorlist{\@toc@elt{#1}}}
\def\@toc@rewrite@authorlist{%
   \let\@toc@authors\@empty
   \@toc@leaderskip\z@
   \let\@set@toc@leaderskip\@set@toc@leaderskip@
   \@tempcnta\count@
   \let\@toc@elt\@toc@rewrite@authorlist@elt
   \@toc@addbreakfalse
   \let\@toc@separator\@empty
   \def\@toc@break@separator{\unskip\break\null\tocleader}%
   \@toc@authorlist}
\newif\if@toc@addbreak
\def\@toc@rewrite@authorlist@elt#1{%
   \def\@tempa{#1}%
   \ifx\@tempa\@cs@break
      \@toc@addbreaktrue
   \else
      \@set@toc@leaderskip{#1}%
      \if@toc@addbreak
         \let\@toc@tempb\@toc@break@separator
         \@toc@addbreakfalse
      \else
         \let\@toc@tempb\@toc@separator
      \fi
      \expandafter\def\expandafter\@toc@tempa\expandafter{%
         \@toc@tempb\hbox{#1}}%
      \@csc@t\@toc@authors\@toc@authors\@toc@tempa
      \advance\@tempcnta\m@ne
      \ifnum\@tempcnta>\@ne%%% \@tempcnta: number of remaining author(s)
         \def\@toc@separator{, }%
         \def\@toc@break@separator{,\hfil\break}%
      \else
         \edef\@toc@separator{%
            \ifnum\count@>\tw@ ,\fi%%% This comma should be removed.
            \ and }%
         \edef\@toc@break@separator{%
            \ifnum\count@>\tw@ ,\fi%%% This comma should be removed.
            \hfil\break and }%
      \fi
   \fi}
\newdimen\@toc@leaderskip
\def\@set@toc@leaderskip@#1{%
   \setbox\z@\hbox{#1}%
   \@toc@leaderskip\wd\z@
   \let\@set@toc@leaderskip\@gobble}
\def\@toc@leader{%
   \hskip \z@ \@plus 3em \penalty-\@medpenalty
   \hskip \z@ \@plus-3em
   \ifdim\@toc@leaderskip>\z@
      \leaders
         \copy\@toc@leader@dot
         \hskip 6\wd\@toc@leader@dot\@plus\@toc@leaderskip
      \penalty-\@lowpenalty
      \hskip -\wd\@toc@leader@dot \@plus-\@toc@leaderskip\null
   \fi
   \leaders\copy\@toc@leader@dot\hfill
   \nobreak
   \@toc@leaderskip\z@}
\newbox\@toc@leader@dot
\normalfont
\setbox\z@\hbox{$\m@th\mkern \@dotsep mu\hbox{.}\mkern \@dotsep mu$}
\@tempdima\textwidth \@tempdimb\wd\z@
\advance\@tempdima.5\@tempdimb
\divide\@tempdima\@tempdimb
\count@\@tempdima
\@tempdima\textwidth \divide\@tempdima\count@
\setbox\@toc@leader@dot\hbox to\@tempdima{\hss\unhbox\z@\hss}
\def\tocleader{%
   \null\nobreak
   \leaders\copy\@toc@leader@dot\hfill
   \nobreak\null}
\def\@csc@t#1#2#3{%
   \expandafter\expandafter\expandafter\def
   \expandafter\expandafter\expandafter#1%
   \expandafter\expandafter\expandafter{\expandafter#2#3}}
\let\@@lineno\@empty
\expandafter\ifx\csname inputlineno\endcsname\relax\else
   \ifnum\inputlineno<\z@\else
      \def\@@lineno{l.\the\inputlineno\space}
   \fi
\fi
\def\l@section{\@dottedtocline{1}{20pt}{18pt}}
\def\l@subsection{\@dottedtocline{2}{-38pt}{20pt}}
\def\l@subsubsection{\@dottedtocline{3}{-58pt}{20pt}}
\def\l@paragraph{\@dottedtocline{4}{-78pt}{20pt}}
\def\l@subparagraph{\@dottedtocline{5}{-98pt}{20pt}}
\def\@localtoc@pnumwidth{12pt}
\def\@dottedtocline#1#2#3#4#5{%
   \ifnum#1>\c@tocdepth\else
      \ifhmode \unskip\par \fi
      \ifnum#1=\@ne%%% section
         \medskip
      \fi
      \begingroup
      \@tempdimb#2\relax
      \ifdim\@tempdimb<\z@
         \def\@numberline@adjust{\hfill}%
         \@tempdimb-\@tempdimb
      \else
         \let\@numberline@adjust\@empty
      \fi
      \@tempdima#3\relax
      \leftskip\@tempdima \advance\leftskip\@tempdimb
      \rightskip\@localtoc@pnumwidth\relax
      \parfillskip-\rightskip \advance\rightskip 20\p@
      \noindent
      \hskip-\@tempdima
      #4\nobreak\tocleader\nobreak
      \setbox\z@\hbox{#5}%
      \ifdim\@localtoc@pnumwidth<\wd\z@\else
         \setbox\z@\hbox to\@localtoc@pnumwidth{\hss\unhbox\z@}%
      \fi
      \box\z@
      \par
      \endgroup
   \fi}
\def\numberline#1{%
   \setbox\z@\hbox{\@numberline@adjust#1}%
   \advance\@tempdima -1em\relax
   \ifdim\wd\z@>\@tempdima\else
      \setbox\z@\hbox to\@tempdima{\unhbox\z@\hss}%
   \fi
   \box\z@\kern1em\relax}
\def\footnoterule{}
\@addtoreset{footnote}{@article}
\long\def\@makefntext#1{%
    \par
     \fontfamily{\rmdefault}\fontsize{7.5}{8}\selectfont %%%08D14
    \leavevmode\hspace*{1em}\@hangfrom{\hbox to 5.5\p@{\@makefnmark\hss}}#1}
\def\footnotemark{%
   \@ifnextchar[%
      \@xfootnotemark
     {\stepcounter{footnote}%
      \protected@xdef\@thefnmark{\thefootnote}%
      \@footnotemark}}
\def\@xfootnotemark[#1]{%
   \protected@edef\@thefnmark{#1}%
   \@footnotemark}
\def\@footnotemark{%
   \ifvmode \leavevmode \fi
   \edef\@x@sf{\the\spacefactor}\nobreak
   \@makefnmark
   \spacefactor\@x@sf
   \relax}
\def\footnotetext{%
   \@ifnextchar[%
      \@xfootnotenext
     {\protected@xdef\@thefnmark{\thempfn}%
      \@footnotetext}}
\def\@xfootnotenext[#1]{%
   \protected@edef\@thefnmark{#1}%
   \@footnotetext}
%
%%% leaders
\def\hrulefill{\leaders\hrule\hfill\kern\z@}
\def\dotfill{\cleaders\hbox{$\m@th \mkern1.5mu.\mkern1.5mu$}\hfill\kern\z@}
%
%%% astronomical symbols
\def\useastrosym{%
   \relax
   \ifmmode
      \expandafter\@use@astrosym@in@math
   \else
      \expandafter\@use@astrosym@in@text
   \fi}
\def\@use@astrosym@in@text#1{%
   \ifvmode \leavevmode \fi
   \begingroup
   \@use@astrosym@\@find@astrosym@text@offset{1}{#1}%
   \endgroup}
\def\@use@astrosym@in@math#1{%
   \mathchoice
      {\@use@astrosym@\@find@astrosym@math@offset{1}{#1}}%
      {\@use@astrosym@\@find@astrosym@math@offset{1}{#1}}%
      {\@use@astrosym@\@find@astrosym@math@offset\defaultscriptratio{#1}}%
      {\@use@astrosym@\@find@astrosym@math@offset
                      \defaultscriptscriptratio{#1}}}
\def\@use@astrosym@#1#2#3{%
   \hbox{%
      #1%
      \advance\count@#3\relax
      \edef\@astro@symbolcode{\the\count@}%
      \dimen@\f@size\p@ \dimen@#2\dimen@
      \@astrosym@getchar}}
\def\@find@astrosym@text@offset{%
   \edef\@tempa{\expandafter\@car\bfdefault\@empty\@nil}%
   \edef\@tempb{\expandafter\@car\f@series\@empty\@nil}%
   \ifx\@tempa\@tempb
      \count@100\relax
   \else
      \edef\@tempa{\sfdefault}%
      \ifx\@tempa\f@family
         \count@200\relax
      \else
         \count@\z@
      \fi
   \fi}
\def\@find@astrosym@math@offset{%
   \def\@tempa{bold}%
   \ifx\@tempa\math@version \count@100\relax
   \else                    \count@\z@        \fi}
\DeclareRobustCommand*\Sol{\ensuremath{\@solar}}
\def\@solar{\mathbin{\mathchoice{\@@solar}{\@@solar}{\odot}{\odot}}}
\def\@@solar{%
   \hbox{%
      \dimen@\f@size\p@
      \@tempdima.6\dimen@ \@tempdimb.4667\dimen@
      \advance\@tempdima.5\p@ \advance\@tempdimb.5\p@
      \divide\@tempdima\p@ \divide\@tempdimb\p@
      \@tempcnta\@tempdima \@tempcntb\@tempdimb
      \ifnum\@tempcnta<\@ne \@tempcnta\@ne \fi
      \ifnum\@tempcnta>15   \@tempcnta15  \fi
      \advance\@tempcnta95\relax
      \ifnum\@tempcntb<\@ne \@tempcntb\@ne \fi
      \ifnum\@tempcntb>15   \@tempcntb15  \fi
      \advance\@tempcntb111\relax
      \kern.5\dimen@
      \raise.2\dimen@\hbox to\z@{\tencirc\char\@tempcnta\hss}%
      \raise.2\dimen@\hbox to\z@{\fivecirc\char\@tempcntb\hss}%
      \kern.5\dimen@}}
\edef\@tempa{\fontname\tencirc\space at5pt}
\font\fivecirc\@tempa\relax
\DeclareRobustCommand*\Astrofont{\useastrosym{0}}
\if@mfastrosym %%% use METAFONT version
\DeclareFontFamily{U}{astro}{}
\begingroup
\nfss@catcodes
\ifx\@astrofont\@empty \def\@astrofont{astrosym}\fi
\edef\x{\noexpand\DeclareFontShape{U}{astro}{m}{n}%
   {<-> s * [.9] \@astrofont}{}}
\expandafter\endgroup\x
\def\@astrosym@getchar{%
   \fontsize\dimen@\z@
   \usefont{U}{astro}{m}{n}%
   \char\@astro@symbolcode}
\else
\def\@astrosym@getchar{%
   \@tempdima.01875\dimen@ %%% \f@size = 10 ==> 1dot = 3/16 pt
   \dimen@1.5\@tempdima
   \setbox\z@\hbox{%
      \setbox\z@\hbox{%
         \let\@\@foc@ \def\@@##1{\gdef\@astrosym@shift{##1}}%
         \@nameuse{@astrosym@\@astro@symbolcode}}%
      \lower\@astrosym@shift\dimen@\box\z@}%
   \dp\z@\z@ \box\z@}
\def\@foc@#1{%
   \@tempcnta\z@
   \hbox to \@tempdima\bgroup\vbox\bgroup\@@foc@loop#1,-1,}
\def\@@foc@loop#1,{%
   \ifnum#1<\z@
      \let\@tempa\@@foc@end
   \else
      \ifodd\@tempcnta \let\@tempa\@@foc@
      \else            \let\@tempa\@@foc@blank \fi
   \fi
   \@tempa{#1}}
\def\@@foc@end#1{%
   \hrule\@width\@tempdima\@height\z@
   \egroup\egroup\ignorespaces}
\def\@@foc@#1{%
   \hrule\@height#1\@tempdima
   \advance\@tempcnta\@ne
   \@@foc@loop}
\def\@@foc@blank#1{%
   \kern#1\@tempdima
   \advance\@tempcnta\@ne
   \@@foc@loop}
\fi
%
%%% font data of astrosym (about 1000 lines)
\@namedef{@astrosym@0}{\@@{0}%
   \@{21,9,19}\@{18,15,16}\@{16,19,14}\@{14,23,12}\@{13,25,11}%
   \@{11,29,9}\@{10,12,7,12,8}\@{9,10,13,10,7}\@{8,9,17,9,6}%
   \@{7,8,21,8,5}\@{6,8,23,8,4}\@{6,7,25,7,4}\@{5,7,27,7,3}%
   \@{5,6,29,6,3}\@{4,7,29,7,2}\@{4,6,31,6,2}\@{3,7,31,7,1}%
   \@{3,6,33,6,1}\@{3,6,33,6,1}\@{2,6,35,6}\@{2,6,16,3,16,6}%
   \@{2,6,15,1,3,1,15,6}\@{2,6,14,1,5,1,14,6}\@{2,6,14,1,5,1,14,6}%
   \@{2,6,14,1,5,1,14,6}\@{2,6,15,1,3,1,15,6}\@{2,6,16,3,16,6}%
   \@{2,6,35,6}\@{3,6,33,6,1}\@{3,6,33,6,1}\@{3,7,31,7,1}\@{4,6,31,6,2}%
   \@{4,7,29,7,2}\@{5,6,29,6,3}\@{5,7,27,7,3}\@{6,7,25,7,4}\@{6,8,23,8,4}%
   \@{7,8,21,8,5}\@{8,9,17,9,6}\@{9,10,13,10,7}\@{10,12,7,12,8}\@{11,29,9}%
   \@{13,25,11}\@{14,23,12}\@{16,19,14}\@{18,15,16}\@{21,9,19}\@{49}}
%%% end of font data
%
%%% miscellaneous symbols
\let\solar\Sol
\DeclareRobustCommand*\MO{%%% solar mass
   \relax\ifmmode\@math@sub@solar{M}\else\@text@sub@solar{M}\fi}
\let\Mo\MO
\DeclareRobustCommand*\LO{%%% solar luminosity
   \relax\ifmmode\@math@sub@solar{L}\else\@text@sub@solar{L}\fi}
\DeclareRobustCommand*\RO{%%% solar radius
   \relax\ifmmode\@math@sub@solar{R}\else\@text@sub@solar{R}\fi}
\def\@math@sub@solar#1{{{#1}_{\solar}}}
\def\@text@sub@solar#1{%
   \ifvmode\leavevmode\fi
   \hbox{$\m@th{#1}_{\solar}$}}
\if@useamsfonts
   \RequirePackage{amssymb}
\else
   \def\lesssim{\mathcomposite[4]\mathrel<\sim}
   \def\gtrsim{\mathcomposite[4]\mathrel>\sim}
   \def\leqq{\mathcomposite[3]\mathrel<=}
   \def\geqq{\mathcomposite[3]\mathrel>=}
   \def\lessgtr{\mathcomposite[-2]\mathrel<>}
   \def\gtrless{\mathcomposite[-2]\mathrel><}
   \def\lessapprox{\mathcomposite[2]\mathrel<\approx}
   \def\gtrapprox{\mathcomposite[2]\mathrel>\approx}
   \def\leftrightarrows{\mathcomposite\mathrel\gets\to}
   \def\square{\Box}
   \def\varnothing{\mathcomposite*\mathord\bigcirc{\big/}}
\fi
\def\D{\mathrm{d}}
\def\intkern@{\mkern-6mu\mathchoice{\mkern-3mu}{}{}{}}
\def\intdots@{%
   \mathchoice
      {{\cdotp\cdotp\cdotp}}%
      {{\cdotp}\mkern1.5mu{\cdotp}\mkern1.5mu{\cdotp}}%
      {{\cdotp}\mkern1mu{\cdotp}\mkern1mu{\cdotp}}%
      {{\cdotp}\mkern1mu{\cdotp}\mkern1mu{\cdotp}}}
\def\iint{\intop\intkern@\intop\nolimits}
\def\iiint{\intop\intkern@\intop\intkern@\intop\nolimits}
\def\iiiint{\intop\intkern@\intop\intkern@\intop\intkern@\intop\nolimits}
\def\idotsint{\intop\intdots@\intop\nolimits}
\def\hateqq{\mathrel{\widehat=}}
\def\simless{\mathcomposite[-2]\mathrel\sim<}
\def\simgtr{\mathcomposite[-2]\mathrel\sim>}
\def\lesssimeq{\mathcomposite\mathrel<{\mathcomposite[-6]\mathrel\sim-}}
\def\gtrsimeq{\mathcomposite\mathrel>{\mathcomposite[-6]\mathrel\sim-}}
\let\ltsim\lesssim
\let\gtsim\gtrsim
\let\getsto\leftrightarrows
\def\diameter{\ensuremath{\varnothing}}
\def\earth{\ensuremath{\oplus}}
\def\singlebond{\@makechembond\@ne}
\def\doublebond{\@makechembond\tw@}
\def\triplebond{\@makechembond\thr@@}
\let\sbond\singlebond
\let\dbond\doublebond
\let\tbond\triplebond
\def\@makechembond{\relax
   \ifmmode \expandafter\@math@makechembond
   \else    \expandafter\@text@makechembond \fi}
\def\@math@makechembond#1{%
   \mathchoice
      {\@makechembond@{#1}\@ne}%
      {\@makechembond@{#1}\@ne}%
      {\@makechembond@{#1}\defaultscriptratio}%
      {\@makechembond@{#1}\defaultscriptscriptratio}}
\def\@text@makechembond#1{\@makechembond@{#1}\@ne}
\def\@makechembond@#1#2{%
   \hbox{%
      \count@#1\relax
      \@tempdima .16667ex \@tempdima#2\@tempdima
      \@tempdimb .1em     \@tempdimb#2\@tempdimb
      \kern\@tempdimb
      \dimen@ -\@tempdima \multiply\dimen@\count@
      \advance\dimen@ 5.7\@tempdima %%% .95ex x ((scaling factor))
      \raise\dimen@\vbox{%
         \hrule\@height\@tempdima \@width 8\@tempdimb
         \loop \ifnum\count@ > \@ne
            \kern\@tempdima
            \hrule\@height\@tempdima \@width 8\@tempdimb
            \advance\count@\m@ne
         \repeat}%
      \kern\@tempdimb}}
\def\mathcomposite{%
   \@ifstar
      {\def\@mathcomposite@option{%
          \baselineskip\z@skip\lineskiplimit-\maxdimen}%
       \@mathcomposite}%
      {\let\@mathcomposite@option\offinterlineskip\@mathcomposite}}
\def\@mathcomposite{%
   \@ifnextchar[\@@mathcomposite{\@@mathcomposite[0]}}
\def\@@mathcomposite[#1]#2#3#4{%
   #2{\mathchoice
      {\@mathcomposite@{#1}{#3}{#4}\displaystyle{1}}%
      {\@mathcomposite@{#1}{#3}{#4}\textstyle{1}}%
      {\@mathcomposite@{#1}{#3}{#4}\scriptstyle\defaultscriptratio}%
      {\@mathcomposite@{#1}{#3}{#4}%
       \scriptscriptstyle\defaultscriptscriptratio}}}
\def\@mathcomposite@#1#2#3#4#5{%
   \vcenter{\m@th\@mathcomposite@option
      \dimen@\f@size\p@\dimen@#1\dimen@\dimen@#5\dimen@
      \divide\dimen@ 18 %%% \dimen@ is about #1 x #5 mu
      \edef\@mathcomposite@skipamount{\the\dimen@}%
      \ialign{\hfil$#4##$\hfil\cr
         #2\crcr\noalign{\vskip\@mathcomposite@skipamount}%
         #3\crcr}}}
\DeclareRobustCommand*\boldsymbol[1]{%
   \begingroup
   \mathchoice
      {\hbox{\mathversion{bold}$\m@th\displaystyle#1$}}%
      {\hbox{\mathversion{bold}$\m@th\textstyle#1$}}%
      {\hbox{\mathversion{bold}$\m@th\scriptstyle#1$}}%
      {\hbox{\mathversion{bold}$\m@th\scriptscriptstyle#1$}}%
   \endgroup}
\DeclareRobustCommand*\textbackslash{%
   \@nomath\textbackslash
   \ifmmode
      \backslash
   \else
      \edef\@tempa{\ttdefault}%
      \ifx\@tempa\f@family
         \begingroup\fontencoding{OT1}\selectfont\char'134\endgroup
      \else
         \begingroup\fontencoding{OMS}\selectfont\char'156\endgroup
      \fi
   \fi}
\DeclareRobustCommand*\atom{%
   \ifmmode \expandafter\@math@atom
   \else    \expandafter\@text@atom \fi}
\def\@text@atom#1#2#3{\ensuremath{\@atom\scriptstyle{#1}{#2}{#3}}}
\def\@math@atom#1#2#3{%
   \mathchoice
      {\@atom\scriptstyle{#1}{#2}{#3}}%
      {\@atom\scriptstyle{#1}{#2}{#3}}%
      {\@atom\scriptscriptstyle{#1}{#2}{#3}}%
      {\@atom\scriptscriptstyle{#1}{#2}{#3}}}
\def\@atom#1#2#3#4{%
   \begingroup
   \setbox\z@\hbox{$\m@th#1#3$}%
   \setbox\tw@\hbox{$\m@th#1#4$}%
   \ifdim\wd\z@<\wd\tw@ \dimen@\wd\tw@
   \else                \dimen@\wd\z@  \fi
   {\vphantom{#2}}_{\hbox to\dimen@{\hss\unhbox\z@}}%
                  ^{\hbox to\dimen@{\hss\unhbox\tw@}}%
   \nobreak
   \mathrm{#2}%
   \endgroup}
\DeclareRobustCommand*\emissiontype{%
   \relax
   \ifmmode \expandafter\@math@emissiontype
   \else    \expandafter\@text@emissiontype
   \fi}
\def\@text@emissiontype#1{%
   \ifvmode \leavevmode \fi
   \unskip\nobreak\,\nobreak
   \@@emissiontype\f@size{#1}}
\def\@math@emissiontype#1{%
   \nobreak\,\nobreak
   \mathchoice
      {\@@emissiontype\tf@size{#1}}%
      {\@@emissiontype\tf@size{#1}}%
      {\@@emissiontype\sf@size{#1}}%
      {\@@emissiontype\ssf@size{#1}}}
\def\@@emissiontype#1#2{%
   \hbox{\dimen@#1\p@ \dimen@.8\dimen@
      \ifdim\dimen@<4\p@ \dimen@4\p@ \fi
      \fontsize\dimen@\f@baselineskip\selectfont
      #2}}
\newcount\leftroot@
\newcount\uproot@
\def\leftroot{\@latexerr{Invalid \string\leftroot}\@eha}
\def\uproot{\@latexerr{Invalid \string\uproot}\@eha}
\DeclareRobustCommand*\sqrt{%
   \bgroup
   \leftroot@\z@ \uproot@\z@
   \@ifnextchar[\@osqrt\@nsqrt}
\DeclareRobustCommand*\safesqrt{%
   \bgroup
   \let\@makesqrt\@noadjust@makesqrt
   \leftroot@\z@ \uproot@\z@
   \@ifnextchar[\@osqrt\@nsqrt}
\def\@nsqrt#1{\mathpalette\@makesqrt{#1}\egroup}
\def\@osqrt[#1]#2{\root #1\of{#2}\egroup}
\def\root#1\of{%
   \@get@root@shift#1\@nnil
   \setbox\rootbox\hbox{$\m@th\scriptscriptstyle{\@tempa}$}%
   \mathpalette\r@@t}
\def\@get@root@shift{\futurelet\let@token\@get@root@shift@}
\def\@get@root@shift@{%
   \def\next@{\@collect@root}%
   \ifx     \let@token\uproot   \def\next@{\@get@uproot}%
   \else\ifx\let@token\leftroot \def\next@{\@get@leftroot}%
   \else\ifx\let@token\@sptoken \def\next@{\@get@space@in@root}%
   \fi\fi\fi
   \next@}
\def\@get@uproot#1\uproot#2{%
   \advance\uproot@#2\relax
   \@get@root@shift}
\def\@get@leftroot#1\leftroot#2{%
   \advance\leftroot@#2\relax
   \@get@root@shift}
\begingroup
\def\:{\def\@get@space@in@root}
\expandafter\endgroup\: {\@get@root@shift}
\def\@collect@root#1\@nnil{\def\@tempa{#1}}
\def\r@@t#1#2{%
   \setbox\z@\hbox{$\m@th\@makesqrt{#1}{#2}$}%
   \dimen@\ht\z@ \advance\dimen@-\dp\z@
   \setbox\tw@\hbox{$\m@th#1\mskip\uproot@ mu$}%
   \advance\dimen@ by1.667\wd\tw@
   \mkern-\leftroot@ mu\mkern5mu
   \raise.6\dimen@\copy\rootbox
   \mkern-10mu\mkern\leftroot@ mu
   \box\z@}
\def\@@makesqrt#1#2{%
   \setbox\z@\hbox{$\m@th#1#2$}%
   \setbox\tw@\hbox{$\m@th#1\mkern50mu$}%
   \dimen@\wd\tw@ \@tempdima\dimen@
   \advance\dimen@-\ht\z@ \advance\dimen@-\dp\z@
   \ifdim\dimen@<\z@
      \setbox\tw@\hbox{$\m@th#1\fixedsqrtsign$}%
      \dimen@\f@size\p@
      \ifx#1\scriptscriptstyle \dimen@\defaultscriptscriptratio\dimen@ \fi
      \ifx#1\scriptstyle       \dimen@\defaultscriptratio\dimen@       \fi
      \dimen@.125\dimen@
      \advance\dimen@\ht\z@ \advance\dimen@\dp\z@
      \advance\dimen@-\dp\tw@ \divide\dimen@ 5\relax
      \ifdim\dimen@>\z@
         \@tempdima\dimen@ \ifdim\@tempdima<\tw@\p@ \@tempdima\tw@\p@ \fi
         \advance\dimen@.1\p@
         \advance\dimen@-\@tempdima \@tempdimb5\dimen@
         \edef\@tempa{%
            \kern\the\dimen@
            \raise\the\@tempdimb
            \hbox{\noexpand\line(1,5){\strip@pt\@tempdima}}}%
      \else
         \let\@tempa\@empty
      \fi
      \@tempdima\dp\tw@ \advance\@tempdima-\dp\z@
      \advance\@tempdima-\ht\tw@
      \setbox\tw@\hbox{%
         \unitlength\p@
         \box\tw@
         \@tempa}%
      \raise\@tempdima\box\tw@\nobreak\overline{\box\z@}%
   \else
      {#1\sqrtsign{#2}}%
   \fi}
\def\@noadjust@makesqrt#1#2{{#1\sqrtsign{#2}}}
\let\@makesqrt\@@makesqrt
\DeclareMathSymbol\fixedsqrtsign\mathord{largesymbols}{'163}
%
%%% some abbreviations
\def\LETTERLABEL{{\LARGE  Letter} \\ [8pt] }
\def\REVIEWLABEL{{\LARGE  Review} \\ [8pt]}
\def\arcdeg{\ensuremath{{}^{\circ}}}
\let\degree\arcdeg
\def\arcmin{\ensuremath{{}^{\prime}}}
\def\arcsec{\ensuremath{{}^{\prime\prime}}}
\def\farcm@mss{\ensuremath{.\mkern-4mu{}^{\prime}}}%
\let\farcm\farcm@mss
\def\farcs@mss{\ensuremath{.\!\!{}^{\prime\prime}}}%
\let\farcs\farcs@mss
\def\fp{\ensuremath{.\!\!^{\scriptscriptstyle\mathrm{p}}}%
   \ambiguouswarn{fp}{timeform}}
\def\fd{\ensuremath{.\!\!^{\mathrm{d}}}\ambiguouswarn{fd}{timeform}}
\def\fh{\ensuremath{.\!\!^{\mathrm{h}}}\ambiguouswarn{fh}{timeform}}
\def\fm{\ensuremath{.\!\!^{\mathrm{m}}}\ambiguouswarn{fs}{timeform}}
\def\fs{\ensuremath{.\!\!^{\mathrm{s}}}\ambiguouswarn{fm}{timeform}}
\def\fdg{\ensuremath{.\!\!^{\circ}}\ambiguouswarn{fdg}{timeform}}
\def\ubvr{\mbox{$U\!BV\!R$}\ambiguouswarn{ubvr}{ensuremath{UBVR}}}
\def\ub{\mbox{$U\!-\!B$}\ambiguouswarn{ub}{ensuremath{U-B}}}
\def\bv{\mbox{$B\!-\!V$}\ambiguouswarn{bv}{ensuremath{B-V}}}
\def\vr{\mbox{$V\!-\!R$}\ambiguouswarn{vr}{ensuremath{V-R}}}
\def\ur{\mbox{$U\!-\!R$}\ambiguouswarn{ur}{ensuremath{U-R}}}
\def\onehalf{\ensuremath{\frac{1}{2}}}
\def\onethird{\ensuremath{\frac{1}{3}}}
\def\twothirds{\ensuremath{\frac{2}{3}}}
\def\onequarter{\ensuremath{\frac{1}{4}}}
\def\threequarters{\ensuremath{\frac{3}{4}}}
\def\micron{\ensuremath{\mu\mathrm{m}}}
\DeclareRobustCommand\ambiguouswarn[2]{%
   \typeout{\@@lineno Warning [pasj]: ^^J\@spaces
The use of ambiguous command `\@backslashchar#1' is not recommended.^^J%
\@spaces Use `\@backslashchar#2' in place of `\@backslashchar#1'.}}
%
%%% timeform
\DeclareRobustCommand\timeform[1]{\@timeform\timeform{#1}}
\DeclareRobustCommand\TF[1]{\@timeform\TF{#1}}
\def\@timeform#1#2{{%
   \def\@timeform@csname{#1}%
   \begingroup
   \def\circ{D}\def\deg{D}\def\prime{'}%
   \let\rm\@empty \let\mathrm\@empty
   \let~\@empty
   \def\pm{\@other@tilde P}%
   \def\mp{\@other@tilde M}%
   \let\protect\noexpand
   \edef\@tempa{\def\noexpand\@tempb{#2}}%
   \expandafter\endgroup\@tempa
   \@onelevel@sanitize\@tempb
   \let\@tempa\@empty
   \expandafter\@timeform@preprocess\@tempb\@nil
   \let\@timeform@body\@empty
   \let\@timeform@prevdigits\@empty
   \let\@timeform@lastdigits\@empty
   \let\@timeform@lastunit\@empty
   \@chclass\m@ne
   \@lastchclass\m@ne
   \let\@templist\@empty
   \let\protect\@unexpandable@protect
   \expandafter\@timeform@loop@\@tempa\@nil
   \ifx\@timeform@lastunit\@empty \def\@timeform@lastunit{\ }\fi
   \let\protect\relax
   \@timeform@body}}
\def\@timeform@preprocess#1{%
   \def\@tempb{#1}%
   \ifx\@tempb\@nnil\else
      \if \@charlb#1\relax \let\@tempb\@empty \fi
      \if \@charrb#1\relax \let\@tempb\@empty \fi
      \if ^#1\relax        \let\@tempb\@empty \fi
      \edef\@tempa{\@tempa\@tempb}%
      \expandafter\@timeform@preprocess
   \fi}
\begingroup
\catcode`\~=12
\def\x{\def\@other@tilde{~}}
\expandafter\endgroup\x
\def\@timeform@loop@#1{%
   \ifnum\@chclass=\z@ \ifx\@currchar\@empty\else
      \typeout{%
         \@@lineno Warning [pasj]: Invalid character `\@currchar' in
         \expandafter\string\@timeform@csname.}%
   \fi\fi
   \def\@currchar{#1}%
   \@timeform@check@char
   \@timeform@loop}
\def\@timeform@loop{%
   \ifnum\@chclass<\z@
      \ifx\@timeform@prevdigits\@empty
         \let\@tempa\@timeform@lastdigits
      \else
         \toks@\expandafter{\@timeform@lastunit}%
         \edef\@tempa{%
            \@timeform@prevdigits
            \noexpand\@timeform@unit{\the\toks@}%
            \@timeform@lastdigits}%
      \fi
      \@csc@t\@timeform@body\@timeform@body\@tempa
   \else
      \expandafter\expandafter
      \csname @timeform@loop@\romannumeral\@chclass\endcsname
   \fi}
\def\@timeform@check@char{%
   \ifx\@currchar\@nnil
      \@chclass\m@ne
   \else
      \expandafter\count@\expandafter=\expandafter`\@currchar\relax
      \@chclass\z@
      \ifnum`0>\count@\else \ifnum`9<\count@\else
         \@chclass\@ne
      \fi\fi
      \if +\@currchar\relax
         \@chclass\@ne
         \def\@currchar{\protect\ensuremath{+}}%
      \fi
      \if -\@currchar\relax
         \@chclass\@ne
         \def\@currchar{\protect\ensuremath{-}}%
      \fi
      \if D\@currchar\relax \@chclass\tw@ \def\@currchar{\circ}\fi
      \if d\@currchar\relax \@chclass\tw@ \fi
      \if h\@currchar\relax \@chclass\tw@ \fi
      \if m\@currchar\relax \@chclass\tw@ \fi
      \if p\@currchar\relax
         \@chclass\tw@
         \def\@currchar{\scriptscriptstyle p}%
      \fi
      \if s\@currchar\relax \@chclass\tw@ \fi
      \if '\@currchar\relax \@chclass\thr@@ \fi
      \if "\@currchar\relax \@chclass\thr@@ \fi
      \if .\@currchar\relax \@chclass4\relax \fi
      \if \@other@tilde\@currchar\relax \@chclass5\relax \fi
   \fi}
\def\@timeform@loop@i#1{%
   \edef\@templist{\@templist\@currchar}%
   \def\@currchar{#1}%
   \@timeform@check@char
   \ifnum\@chclass<\z@
      \ifx\@timeform@lastdigits\@empty
         \let\@tempa\@templist
      \else
         \toks@\expandafter{\@timeform@lastunit}%
         \edef\@tempa{%
            \@timeform@lastdigits
            \noexpand\@timeform@unit{\the\toks@}%
            \@templist}%
      \fi
      \@csc@t\@timeform@body\@timeform@body\@tempa
      \let\@timeform@next\relax
   \else
      \ifnum\@chclass=\@ne
         \def\@timeform@next{\@timeform@loop@i}%
      \else
         \@lastchclass\@ne
         \ifnum 5=\@chclass\else
            \let\@timeform@prevdigits\@timeform@lastdigits
            \let\@timeform@lastdigits\@templist
            \let\@templist\@empty
         \fi
         \def\@timeform@next{\@timeform@loop}%
      \fi
   \fi
   \@timeform@next}
\def\@timeform@loop@ii#1{%
   \ifx\@timeform@lastunit\@empty\else
      \ifnum\@lastchclass=\tw@
         \toks@\expandafter{\@timeform@lastunit}%
         \edef\@tempa{%
            \@timeform@lastdigits
            \noexpand\@timeform@unit{\the\toks@}}%
         \let\@timeform@lastdigits\@empty
      \else
         \toks@\expandafter{\@timeform@lastunit}%
         \edef\@tempa{%
            \@timeform@prevdigits
            \noexpand\@timeform@unit{\the\toks@}}%
         \let\@timeform@prevdigits\@empty
      \fi
      \@csc@t\@timeform@body\@timeform@body\@tempa
   \fi
   \let\@timeform@lastunit\@currchar
   \def\@currchar{#1}%
   \@timeform@check@char
   \ifnum\@chclass<\z@
      \edef\@tempa{%
         \@timeform@lastdigits
         \noexpand\@timeform@unit{\noexpand\@timeform@lastunit}}%
      \@csc@t\@timeform@body\@timeform@body\@tempa
   \else
      \@lastchclass\tw@
      \expandafter\@timeform@loop
   \fi}
\def\@timeform@loop@iii#1{%
   \ifnum\@lastchclass=\thr@@
      \if\@currchar'\relax \def\@tempa{\prime}%
      \else                \def\@tempa{\prime\prime}%
      \fi
      \@csc@t\@templist\@templist\@tempa
   \else
      \ifnum\@lastchclass=\tw@
         \toks@\expandafter{\@timeform@lastunit}%
         \edef\@tempa{%
            \@timeform@lastdigits
            \noexpand\@timeform@unit{\the\toks@}}%
         \let\@timeform@lastdigits\@empty
         \let\@timeform@lastunit\@empty
         \@csc@t\@timeform@body\@timeform@body\@tempa
      \fi
      \if\@currchar'\relax
         \def\@templist{\prime}%
      \else
         \def\@templist{\prime\prime}%
      \fi
   \fi
   \def\@currchar{#1}%
   \@timeform@check@char
   \@lastchclass=\thr@@
   \ifnum\@chclass=\thr@@
      \def\@timeform@next{\@timeform@loop@iii}%
   \else
      \let\@currchar\@templist
      \let\@templist\@empty
      \def\@timeform@next{\@timeform@loop@ii#1}%
   \fi
   \@timeform@next}
\def\@timeform@loop@iv#1{%
   \ifx\@timeform@prevdigits\@empty
      \edef\@tempa{%
         \@timeform@lastdigits
         \noexpand\@timeform@dot}%
   \else
      \toks@\expandafter{\@timeform@lastunit}%
      \edef\@tempa{%
         \@timeform@prevdigits
         \noexpand\@timeform@unit{\the\toks@}%
         \@timeform@lastdigits
         \noexpand\@timeform@dot}%
      \let\@timeform@lastunit\@empty
   \fi
   \@csc@t\@timeform@body\@timeform@body\@tempa
   \let\@timeform@prevdigits\@empty
   \let\@timeform@lastdigits\@empty
   \def\@currchar{#1}%
   \@timeform@check@char
   \ifnum\@chclass<\z@\else
      \@lastchclass4\relax
      \expandafter\@timeform@loop
   \fi}
\def\@timeform@loop@v#1{%
   \def\@currchar{#1}%
   \ifx\@currchar\@nnil
      \ifx\@timeform@lastdigits\@empty
         \let\@tempa\@templist
      \else
         \toks@\expandafter{\@timeform@lastunit}%
         \edef\@tempa{%
            \@timeform@lastdigits
            \noexpand\@timeform@unit{\the\toks@}%
            \@templist}%
      \fi
      \@csc@t\@timeform@body\@timeform@body\@tempa
      \let\@timeform@next\relax
   \else
      \expandafter\ifx\csname @timeform@cmdlist@\@currchar\endcsname\relax
         \let\@currchar\@empty
      \else
         \edef\@currchar{%
            \noexpand\protect\expandafter\noexpand
            \csname @timeform@cmdlist@\@currchar\endcsname}%
      \fi
      \def\@timeform@next{\@timeform@loop}%
      \@lastchclass\@ne
      \@chclass\@ne
   \fi
   \@timeform@next}
\def\@timeform@cmdlist@P{\ensuremath{\pm}}
\def\@timeform@cmdlist@M{\ensuremath{\mp}}
\def\@timeform@unit#1{%
   \ensuremath{%
      \mathchoice
         {\@timeform@unit@\scriptstyle{#1}}%
         {\@timeform@unit@\scriptstyle{#1}}%
         {\@timeform@unit@\scriptscriptstyle{#1}}%
         {\@timeform@unit@\scriptscriptstyle{#1}}}}
\def\@timeform@unit@#1#2{%
   \setbox\z@\hbox{$\m@th#1\mathrm{#2}$}%
   \setbox\tw@\hbox{$\m@th#1\mathrm{m}$}%
   \dimen@\ht\tw@ \advance\dimen@-\ht\z@
   \ifdim\dimen@<\z@ \dimen@\z@ \fi
   {}^{\raise\dimen@\box\z@}}
\def\@timeform@dot{%
   \ensuremath{%
      \mathchoice
         {\@timeform@dot@\displaystyle\scriptstyle}%
         {\@timeform@dot@\textstyle\scriptstyle}%
         {\@timeform@dot@\scriptstyle\scriptscriptstyle}%
         {\@timeform@dot@\scriptscriptstyle\scriptscriptstyle}}%
   \def\@timeform@lastunit{}}
\def\@timeform@dot@#1#2{%
   \rlap{$\m@th#1.$}%
   \mkern1mu\@timeform@unit@#2{\@timeform@lastunit}}
\def\contentsname{Contents}
\def\papersname{Papers}
\def\lettersname{Letters}
\def\errataname{Errata}
\def\listfigurename{List of Figures}
\def\listtablename{List of Tables}
\def\bibname{References}
\def\indexname{Index}
\def\figurename{Fig.}
\def\tablename{Table}
\def\partname{Part}
\def\chaptername{Chapter}
\def\appendixname{Appendix}
\def\abstractname{Abstract}
\def\today{%
   \number\year~%
   \ifcase\month\or
      January\or February\or March\or     April\or   May\or      June\or
      July\or    August\or   September\or October\or November\or December\fi
   ~\number\day}
\def\re{%
   \par
   \hangindent=5mm
   \hangafter=1
   \noindent}
%
%%% fleqn
\def\[{\relax
   \ifmmode\@badmath\else
   \begin{trivlist}%
   \@beginparpenalty\predisplaypenalty
   \@endparpenalty\postdisplaypenalty
   \item[]\leavevmode
      \hbox to\linewidth\bgroup $\m@th\displaystyle %$
         \hskip\mathindent\bgroup
   \fi}
\def\]{\relax
   \ifmmode
      \egroup $\hfil% $
      \egroup
      \end{trivlist}%
   \else
      \@badmath
   \fi}
%% \def\equation{%
%%    \@beginparpenalty\predisplaypenalty
%%    \@endparpenalty\postdisplaypenalty
%%    \refstepcounter{equation}%
%%    \trivlist \item[]\leavevmode
%%    \hbox to\linewidth\bgroup $\m@th% $
%%       \displaystyle
%%       \hskip\mathindent}%
%% \def\endequation{$\hfil % $
%%       \displaywidth\linewidth\hbox{\@eqnnum}%
%%    \egroup
%%    \endtrivlist}
%% \def\eqnarray{%
%%    \stepcounter{equation}%
%%    \def\@currentlabel{\p@equation\theequation}%
%%    \global\@eqnswtrue\m@th
%%    \global\@eqcnt\z@
%%    \tabskip\mathindent
%%    \let\\=\@eqncr
%%    \setlength\abovedisplayskip{\topsep}%
%%    \ifvmode
%%       \addtolength\abovedisplayskip{\partopsep}%
%%    \fi
%%    \addtolength\abovedisplayskip{\parskip}%
%%    \setlength\belowdisplayskip{\abovedisplayskip}%
%%    \setlength\belowdisplayshortskip{\abovedisplayskip}%
%%    \setlength\abovedisplayshortskip{\abovedisplayskip}%
%%    $$\everycr{}\halign to\linewidth% $$
%%    \bgroup
%%       \hskip\@centering
%%       $\displaystyle\tabskip\z@skip{##}$\@eqnsel&%
%%       \global\@eqcnt\@ne
%%       \hfil$\displaystyle{{}##{}}$\hfil&%
%%       \global\@eqcnt\tw@
%%       $\displaystyle{##}$\hfil \tabskip\@centering&%
%%       \global\@eqcnt\thr@@
%%       \hbox to\z@\bgroup\hss##\egroup\tabskip\z@skip\cr}%
%% \def\endeqnarray{%
%%       \@@eqncr
%%    \egroup
%%    \global\advance\c@equation\m@ne$$% $$
%%    \@ignoretrue}
\def\DeclareAbbreviation#1#2{%
   \DeclareRobustCommand*#1{\@journalname{#2}}}
\def\@journalname#1{{\normalfont#1}}
\DeclareAbbreviation\aap{A\&A}
\DeclareAbbreviation\aapr{A\&AR}
\DeclareAbbreviation\aaps{A\&AS}
\DeclareAbbreviation\aj{AJ}
\DeclareAbbreviation\ao{Appl.\ Opt.}
\DeclareAbbreviation\apj{ApJ}
\DeclareAbbreviation\apjl{ApJL}
\DeclareAbbreviation\apjs{ApJS}
\DeclareAbbreviation\aplett{Astrophys.\ Lett.}
\DeclareAbbreviation\apspr{Astrophys.\ Space\ Phys.\ Res.}
\DeclareAbbreviation\apss{Ap\&SS}
\DeclareAbbreviation\araa{ARA\&A}
\DeclareAbbreviation\azh{AZh}
\DeclareAbbreviation\baas{BAAS}
\DeclareAbbreviation\bain{Bull.\ Astron.\ Inst.\ Netherlands}
\DeclareAbbreviation\fcp{Fund.\ Cosmic\ Phys.}
\DeclareAbbreviation\gca{Geochim.\ Cosmochim.\ Acta}
\DeclareAbbreviation\grl{Geophys.\ Res.\ Lett.}
\DeclareAbbreviation\iaucirc{IAU\ Circ.}
\DeclareAbbreviation\icarus{ICARUS}
\DeclareAbbreviation\jatis{J. Astron. Telesc., Instrum. Syst.}
\DeclareAbbreviation\jcp{J.\ Chem.\ Phys.}
\DeclareAbbreviation\jgr{J.\ Geophys.\ Res.}
\DeclareAbbreviation\jqsrt{J.\ Quant.\ Spectrosc.\ Radiat.\ Transfer}
\DeclareAbbreviation\jrasc{JRASC}
\DeclareAbbreviation\memras{MmRAS}
\DeclareAbbreviation\memsai{Mem.\ Soc.\ Astron.\ Italiana}
\DeclareAbbreviation\mnras{MNRAS}
\DeclareAbbreviation\nat{Nature}
\DeclareAbbreviation\nata{Nature\ Astron.}
\DeclareAbbreviation\nphysa{Nucl.\ Phys.\ A}
\DeclareAbbreviation\pasj{PASJ}
\DeclareAbbreviation\pasp{PASP}
\DeclareAbbreviation\physrep{Phys.\ Rep.}
\DeclareAbbreviation\physscr{Phys.\ Scr.}
\DeclareAbbreviation\planss{Planet.\ Space\ Sci.}
\DeclareAbbreviation\pra{Phys.\ Rev.\ A}
\DeclareAbbreviation\prb{Phys.\ Rev.\ B}
\DeclareAbbreviation\prc{Phys.\ Rev.\ C}
\DeclareAbbreviation\prd{Phys.\ Rev.\ D}
\DeclareAbbreviation\pre{Phys.\ Rev.\ E}
\DeclareAbbreviation\prl{Phys.\ Rev.\ Lett.}
\DeclareAbbreviation\qjras{QJRAS}
\DeclareAbbreviation\raa{Res.\ Astron.\ Astronphys.}
\DeclareAbbreviation\skytel{S\&T}
\DeclareAbbreviation\solphys{Sol.\ Phys.}
\DeclareAbbreviation\sovast{Soviet\ Ast.}
\DeclareAbbreviation\ssr{Space\ Sci.\ Rev.}
\DeclareAbbreviation\zap{ZAp}
\DeclareAbbreviation\procspie{Proc.\ SPIE}
\DeclareAbbreviation\aip{AIP Conf.\ Proc.}
\DeclareAbbreviation\asp{ASP Conf.\ Ser.}
\let\astap=\aap
\let\apjlett=\apjl
\let\apjsupp=\apjs
\let\applopt=\ao
\def\dodoi#1{\gdef\@dodoi{#1}}\dodoi{}
\def\doeprint#1{\gdef\@doeprint{#1}}\doeprint{}
\def\doarXiv#1{\gdef\@doarXiv{#1}}\doarXiv{}
%
%%% about graphics
\def\RelativeFigurePath#1{%
   \def\@figurepath{#1}%
   \ifx\@figurepath\@empty \def\@figurepath{.}\fi}
\RelativeFigurePath{}
\def\FigureFile{\@ifstar\@FigureFile\@FigureFile}
\def\@FigureFile(#1,#2)#3{%
   \def\@figfilename{#3}%
   \@onelevel@sanitize\@figfilename
   \begingroup
   \if@pasj@usefigure
      \edef\@@figfilename{\@figurepath/\@figfilename}%
      \openin\@inputcheck \@@figfilename\relax
      \ifeof\@inputcheck
         \typeout{No file `\@@figfilename'.}%
         \let\@@figfilename\@empty
      \fi
      \closein\@inputcheck
   \else
      \let\@@figfilename\@empty
   \fi
   \ifx\@@figfilename\@empty
      \@defaultunits\@tempdima#1mm\relax\@nnil
      \@defaultunits\@tempdimb#2mm\relax\@nnil
      \edef\@tempa{(\strip@pt\@tempdima,\strip@pt\@tempdimb)}%
      \edef\@tempa{%
         \begingroup
         \unitlength\p@
         \noexpand\begin{picture}\@tempa
           \noexpand\put(0,0){\noexpand\@framepicbox\@tempa[c]{%
              \noexpand\footnotesize
              \noexpand\texttt{\@figfilename}}}%
         \noexpand\end{picture}%
         \endgroup}%
   \else
      \@defaultunits\@tempdima#1mm\relax\@nnil
      \@tempdima.35146\@tempdima %%% 1pt = .35146mm
      \edef\@tempa{%
         \noexpand\@saved@includegraphics
            [width=\strip@pt\@tempdima mm,keepaspectratio]%
            {\@@figfilename}}%
   \fi
   \noindent
   \vtop{\kern.5\baselineskip\hbox{\@tempa}}%
   \endgroup}
\if@pasj@usefigure
\RequirePackage[]{graphicx,color}
\let\@saved@includegraphics\includegraphics
%\def\includegraphics{%
%   \typeout{Do not use \string\includegraphics\space directly.
%            Use \string\FigureFile\space for graphics.}%
%   \@saved@includegraphics}
\else
\let\@saved@includegraphics\relax
\fi
\predisplaypenalty\z@
\postdisplaypenalty\z@
\uchyph = 0
\interdisplaylinepenalty\z@
\RequirePackage{latexsym}
\thinmuskip  = 2mu plus 1mu minus 1mu
\medmuskip   = 3mu plus 1mu minus 2mu
\thickmuskip = 4mu plus 2mu minus 2mu
\clubpenalty\@lowpenalty
\widowpenalty\@lowpenalty
\pagestyle{headings}
\pagenumbering{arabic}
\if@twocolumn \twocolumn \else \onecolumn \fi
\AtBeginDocument{\sloppy}
\if@proofread \draft \fi
%%%%%
\def\rhfont{\fontfamily{\sfdefault}\fontsize{8}{9.5}\selectfont}
\def\titlefont{\fontfamily{\sfdefault}\fontsize{18}{22}\selectfont\bfseries}
\def\authorfont{\fontfamily{\sfdefault}\fontsize{11}{15}\selectfont\bfseries}%
\def\affilfont{\reset@font\fontfamily{\sfdefault}\fontsize{9}{10}\selectfont}%
\def\corfont{\reset@font\fontfamily{\sfdefault}\fontsize{8}{9}\selectfont}%
\def\idfont{\reset@font\fontfamily{\sfdefault}\fontsize{7}{8}\selectfont}%%%for orcid
\def\historyfont{\reset@font\fontfamily{\rmdefault}\fontsize{7.5}{9.5}\selectfont}%
\def\abstractfont{\fontfamily{\sfdefault}\fontsize{8}{9}\selectfont}
\def\keywordfont{\fontfamily{\sfdefault}\fontsize{8}{9}\selectfont}
\def\abstractheadfont{\fontfamily{\sfdefault}\fontsize{10}{11}\selectfont\bfseries}
\def\keywordheadfont{\fontfamily{\sfdefault}\fontsize{8}{9}\selectfont\bfseries}
\def\rffont{\fontfamily{\rmdefault}\fontsize{7.5}{9.5}\selectfont}
%%
\def\sectionfont{\fontfamily{\sfdefault}\fontsize{11}{13}\selectfont\bfseries\rightskip0pt plus1fill}
\def\subsectionfont{\fontfamily{\sfdefault}\fontsize{10}{11}\selectfont\rightskip0pt plus1fill}
\def\subsubsectionfont{\fontsize{9}{11}\selectfont\bfseries}
\def\paragraphfont{\fontsize{9}{11}\selectfont\itshape}%
\def\subparagraphfont{\fontfamily{\sfdefault}\fontsize{8.5}{11}\selectfont}%
\def\extractfont{\reset@font\fontfamily{\rmdefault}\fontsize{8.75}{11}\selectfont\leftskip12pt\rightskip12pt}
\def\figcaptionfont{\fontfamily{\sfdefault}\fontsize{7.5}{9.5}\selectfont}
\def\figcaptionnumfont{\fontfamily{\sfdefault}\fontsize{7.5}{9.5}\selectfont\bfseries}
\def\bibliofont{\fontfamily{\rmdefault}\fontsize{8}{10}\selectfont}
%%
\newskip\tableleftskip
\newskip\tablerightskip
\newskip\tablenoteleftskip
\newskip\tablenoterightskip
%%
\def\tablefont{\fontsize{8}{9.5}\selectfont}%
\def\tablecaptionfont{\fontfamily{\sfdefault}\fontsize{7.5}{9.5}\selectfont\leftskip\tableleftskip\rightskip\tablerightskip}% 
\def\tablecaptionnumfont{\fontfamily{\sfdefault}\fontsize{7.5}{9.5}\selectfont\bfseries}% 
\def\TCHfont{\fontsize{8}{9.5}\selectfont}%
\def\TSCHfont{}%
\def\tabnotefont{\fontsize{7.5}{8}\selectfont\hangindent.1pt\leftskip\tableleftskip\rightskip\tablerightskip}% use plus 1fill if needed
\def\rhhfont{\fontfamily{\sfdefault}\fontsize{8}{10}\selectfont\raggedleft}
\def\foliofont{\fontfamily{\sfdefault}\fontsize{8}{10}\selectfont\bfseries}
%%
\def\toprule{\\[-6pt]\hline\\[-4.5pt]}
\def\colrule{\\[-6pt]\hline\\[-4.5pt]}
\def\botrule{\\[-6pt]\hline\\[-8pt]}
%%
\newbox\tempbox
\newdimen\tabledim%
\def\tbl#1#2{%
\setbox\tempbox\hbox{\tablefont#2}%
 \tabledim\hsize
  \advance\tabledim-\wd\tempbox
  \ifdim\tabledim>0pt
     \divide\tabledim2
  \else
     \global\tabledim0pt
  \fi
   \global\tableleftskip\tabledim%%Call Id:390490
   \global\tablerightskip\tabledim plus1fill%%Call Id:390490
  \caption{#1}%
  {\centerline{\box\tempbox}}}%
%%
\renewenvironment{quotation}{\par\addvspace{3.4pt plus2pt}%
      \extractfont\ignorespaces% 
}{%
      \par\addvspace{3.1pt plus2pt}}
%%
\newenvironment{tabnote}{\par\vskip3pt\tabnotefont}{\par}
%%%
\def\jyear#1{\gdef\@jyear{#1}}\jyear{0000}
\def\endpage#1{\gdef\@endpage{#1}}\endpage{0}
\def\doi#1{\gdef\@doi{doi:\ 10.1093/pasj/#1}}\doi{xxx000}
\def\volume#1{\gdef\@jvol{#1}}\volume{00}
\def\Issue#1{\gdef\@Issue{#1}}\Issue{0}
\AtEndDocument{\immediate\write\@mainaux{\string\endpage{\thepage}}}%
\setlength\footskip{20pt}%{24pt}
\setlength{\skip\footins}{12\p@ \@plus 6\p@ \@minus 6\p@}% change + based on FN font height
%
\newenvironment{ack}{\par\section*{Acknowledgments}}{\par}
%%% font
\usepackage[T1]{fontenc}
\renewcommand{\sfdefault}{phv} %{cmss} 
\renewcommand{\rmdefault}{ptm} %{cmr} 
\renewcommand{\ttdefault}{cmtt}
%\usepackage{newtxtext, newtxmath}
%%\raggedbottom
%% ===========================
\let\leftroot\@undefined
\let\uproot\@undefined
\let\iint\@undefined
\let\iiint\@undefined
\let\iiiint\@undefined
\let\idotsint\@undefined
%%%%%%%%%%
\AtBeginDocument{%
  \@ifpackageloaded{amsmath}{}{\usepackage{amsmath}}%
  % --- patch for lineno ---
  \@ifpackageloaded{lineno}{%
    \renewenvironment{equation}{%
      \gdef\withinformula{yes}\begin{linenomath}\incr@eqnum
      \mathdisplay@push
      \st@rredfalse \global\@eqnswtrue
      \mathdisplay{equation}%
    }{%
      \endmathdisplay{equation}%
      \mathdisplay@pop
      \end{linenomath}\gdef\withinformula{no}\ignorespacesafterend}

    \renewenvironment{equation*}{%
      \gdef\withinformula{yes}\begin{linenomath}\mathdisplay@push
      \st@rredtrue \global\@eqnswfalse
      \mathdisplay{equation*}%
    }{%
      \endmathdisplay{equation*}%
      \mathdisplay@pop
      \end{linenomath}\gdef\withinformula{no}\ignorespacesafterend}

    \def\withinformula{no}
    \newcommand*\patchAmsMathEnvironmentForLineno[1]{%
      \expandafter\let\csname old#1\expandafter\endcsname\csname #1\endcsname
      \expandafter\let\csname oldend#1\expandafter\endcsname\csname end#1\endcsname
      \renewenvironment{#1}%
        {\gdef\withinformula{yes}\linenomath\csname old#1\endcsname}%
        {\csname oldend#1\endcsname\endlinenomath\gdef\withinformula{no}}}% 

    \newcommand*\patchBothAmsMathEnvironmentsForLineno[1]{%
      \patchAmsMathEnvironmentForLineno{#1}%
      \patchAmsMathEnvironmentForLineno{#1*}}%

    \patchBothAmsMathEnvironmentsForLineno{align}%
    \patchBothAmsMathEnvironmentsForLineno{flalign}%
    \patchBothAmsMathEnvironmentsForLineno{alignat}%
    \patchBothAmsMathEnvironmentsForLineno{gather}%
    \patchBothAmsMathEnvironmentsForLineno{multline}%
  }{}% end of lineno

  % --- natbib ---
  \let\square\undefined % avoid conflict of amsfonts 
  \@ifpackageloaded{natbib}{%
   \def\bibfont{\bibliofont}%
    \renewcommand{\bibsection}{%
       \begingroup
         \global\@in@appendixfalse 
         \section*{\bibname}%
       \endgroup
       \@mkboth{\MakeUppercase{\bibname}}{\MakeUppercase{\bibname}}%
       \small
    }%
    % fix error of natbib
    \def\NAT@parse@date#1#2#3#4#5#6@@{%
      \ifnum\the\catcode`#1=11\def\NAT@year{}\def\NAT@exlab{#1}\else
      \ifnum\the\catcode`#2=11\def\NAT@year{#1}\def\NAT@exlab{#2}\else
      \ifnum\the\catcode`#3=11\def\NAT@year{#1#2}\def\NAT@exlab{#3}\else
      \ifnum\the\catcode`#4=11\def\NAT@year{#1#2#3}\def\NAT@exlab{#4}\else
      \def\NAT@year{#1#2#3#4}\def\NAT@exlab{{#1#2#3#4#5}}\fi\fi\fi\fi}%
    \renewcommand\NAT@yrsep{,\space}%
    \renewcommand\NAT@aysep{}%
  }{%
    % without natbib
    \providecommand{\bibsection}{%
       \section*{\bibname}%
       \@mkboth{\MakeUppercase{\bibname}}{\MakeUppercase{\bibname}}%
       \small
    }%
  }% 
} % end of AtBeginDocument
%%%%%
\gdef\YES{yes}
\def\withinfirstpage{yes}%
\def\@outputpage{%
\begingroup
  \let \protect \noexpand
  \language\document@default@language
  \@resetactivechars
  \global\let\@@if@newlist\if@newlist
  \global\@newlistfalse
  \@parboxrestore
  \shipout \vbox{%
    \set@typeset@protect
    \aftergroup \endgroup
    \aftergroup \set@typeset@protect
  \if@specialpage
    \global\@specialpagefalse\@nameuse{ps@\@specialstyle}%
  \fi
  \if@twoside
    \ifodd\count\z@ \let\@thehead\@oddhead \let\@thefoot\@oddfoot
         \let\@themargin\oddsidemargin
    \else \let\@thehead\@evenhead
       \let\@thefoot\@evenfoot \let\@themargin\evensidemargin
    \fi
  \fi
  \reset@font
  \normalsize
  \normalsfcodes
  \let\label\@gobble
  \let\index\@gobble
  \let\glossary\@gobble
  \baselineskip\z@skip \lineskip\z@skip \lineskiplimit\z@
    \@begindvi
    \vskip \topmargin
    \moveright\@themargin \vbox {%
      \setbox\@tempboxa \vbox to\headheight{%
        \vfil
        \color@hbox
          \normalcolor
          \hb@xt@\textwidth{\@thehead}%
        \color@endbox
        }%
      \dp\@tempboxa \z@
      \box\@tempboxa
      \vskip \headsep
      \box\@outputbox
      \baselineskip \footskip
      \color@hbox
        \normalcolor
        \hb@xt@\textwidth{\@thefoot}%
      \color@endbox
      }%
    }%
\ifx\withinfirstpage\YES\global\advance\textheight36.5pt\gdef\withinfirstpage{no}\fi%
  \global\let\if@newlist\@@if@newlist
  \global \@colht \textheight
  \stepcounter{page}%
  \let\firstmark\botmark
%%
}
%%
\endinput
%% 
%% Version History
%% Ver. 1.0 (2014 Nov 25/Aptara Inc.) (Based on pasj00.cls)
%% ---------------------
%% 1. Updated for margins to closely match the final composition output.
%% 2. Used the Times for normal text and Helvetica for display heads.
%%
%% Ver. 1.1 (2018 Feb 6) 
%% ---------------------
%% 1. Deleted dvips option   
%% 2. Deleted unnecessary commands 
%% 
%% Ver. 1.2 (2018 May 15) 
%% ---------------------
%% 1. Change default font to "Computer Modern" for normal text 
%% 
%% Ver. 2.0 (2023 Oct 30) 
%% ---------------------
%% 1. Deleted some unnecessary options   
%% 2. Adjust to the updated page design 
%% 
%% Ver. 2.1 (2024 July 01) 
%% ---------------------
%% 1. Add command for ORCID  
%% 2. Update journal abbreviations
%%
%% Ver. 2.1.1 (2024 August 20) 
%% ---------------------
%% 1. Fix error of apppendix title
%%
%% Ver. 2.2 (2026 May 6) 
%% ---------------------
%% 1. Minor adjustments to the page layout
%% 2. Minor revisions to the template and usage files
%% 3. Add some journal abbreviations
%%
%% =============================================
%% End of file `pasj02.cls'.