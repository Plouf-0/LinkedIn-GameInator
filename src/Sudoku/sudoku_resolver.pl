:- use_module(library(clpfd)).

% Areas (boxes) always span 3 columns; the number of rows per area varies
% (e.g. 3 for a 9x9 grid, 2 for a 6x6 grid) and is passed in from Python.
cols_per_area(3).

% Splits a flat list into a list of Size-length rows.
chunk(_, [], []).
chunk(Size, List, [Row|Rows]) :-
    length(Row, Size),
    append(Row, Rest, List),
    chunk(Size, Rest, Rows).

% Replaces each 0 (empty cell) in Puzzle with a free variable in Solution,
% and keeps the other values as they are (these are the known clues).
prep([], []).
prep([0|T], [_|T2]) :- !, prep(T, T2).
prep([X|T], [X|T2]) :- prep(T, T2).

sudoku(Grid, Size, RowsPerArea) :-
    cols_per_area(ColsPerArea),

    append(Grid, Vars),
    Vars ins 1..Size,

    maplist(all_distinct, Grid),
    transpose(Grid, Columns),
    maplist(all_distinct, Columns),

    LastRow is Size - RowsPerArea,
    LastCol is Size - ColsPerArea,
    numlist(0, LastRow, RowStarts0),
    findall(R, (member(R, RowStarts0), 0 is R mod RowsPerArea), RowStarts),
    numlist(0, LastCol, ColStarts0),
    findall(C, (member(C, ColStarts0), 0 is C mod ColsPerArea), ColStarts),

    findall(BlockRow-BlockCol, (member(BlockRow, RowStarts), member(BlockCol, ColStarts)), BlockStarts),

    MaxRowOffset is RowsPerArea - 1,
    MaxColOffset is ColsPerArea - 1,
    findall(DR-DC, (between(0, MaxRowOffset, DR), between(0, MaxColOffset, DC)), Offsets),

    % maplist (unlike findall) does not copy_term its arguments, so the
    % cells extracted below stay the actual Grid variables: all_distinct
    % posted on them really constrains the grid instead of a disconnected copy.
    maplist(post_block_all_distinct(Grid, Offsets), BlockStarts),

    maplist(label, Grid).

post_block_all_distinct(Grid, Offsets, BlockRow-BlockCol) :-
    maplist(block_cell(Grid, BlockRow, BlockCol), Offsets, Block),
    all_distinct(Block).

block_cell(Grid, BlockRow, BlockCol, DR-DC, Cell) :-
    R is BlockRow + DR,
    C is BlockCol + DC,
    nth0(R, Grid, Row),
    nth0(C, Row, Cell).

% Entry point used from Python.
% Puzzle: flat Prolog list of Size*Size integers (0 = empty cell).
% Size: grid width/height (e.g. 9, 6).
% RowsPerArea: number of rows in each area/box (columns per area is always 3).
% Solution: flat solved Puzzle, same length as Puzzle.
resout(Puzzle, Size, RowsPerArea, Solution) :-
    prep(Puzzle, Solution),
    chunk(Size, Solution, Grid),
    sudoku(Grid, Size, RowsPerArea).
