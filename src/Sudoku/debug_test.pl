:- use_module(library(clpfd)).
:- consult('sudoku_resolver.pl').

test :-
    Puzzle = [0,1,2,0,0,0, 3,0,4,0,0,0, 5,6,1,0,0,0, 0,0,0,1,5,6, 0,0,0,2,0,1, 0,0,0,3,4,0],
    prep(Puzzle, Solution),
    chunk(6, Solution, Grid),
    Grid = [R0,R1,R2,R3,R4,R5],
    writeln(before_constraints(Grid)),

    cols_per_area(ColsPerArea),
    append(Grid, Vars),
    Vars ins 1..6,
    maplist(all_distinct, Grid),
    transpose(Grid, Columns),
    maplist(all_distinct, Columns),

    RowsPerArea = 2,
    LastRow is 6 - RowsPerArea,
    LastCol is 6 - ColsPerArea,
    numlist(0, LastRow, RowStarts0),
    findall(R, (member(R, RowStarts0), 0 is R mod RowsPerArea), RowStarts),
    numlist(0, LastCol, ColStarts0),
    findall(C, (member(C, ColStarts0), 0 is C mod ColsPerArea), ColStarts),

    MaxRowOffset is RowsPerArea - 1,
    MaxColOffset is ColsPerArea - 1,
    findall(
        Block,
        (
            member(BlockRow, RowStarts), member(BlockCol, ColStarts),
            findall(
                Cell,
                (
                    between(0, MaxRowOffset, DR),
                    between(0, MaxColOffset, DC),
                    R is BlockRow + DR,
                    C is BlockCol + DC,
                    nth0(R, Grid, Row),
                    nth0(C, Row, Cell)
                ),
                Block
            )
        ),
        Blocks
    ),
    writeln(blocks(Blocks)),
    nth0(0, Blocks, FirstBlock),
    nth0(4, FirstBlock, BlockCellR1C1),

    nth0(1, Grid, RowFetched),
    ( RowFetched == R1 -> writeln(row_same) ; writeln(row_different) ),
    nth0(1, R1, Cell_r1c1),
    ( BlockCellR1C1 == Cell_r1c1 -> writeln(cell_same) ; writeln(cell_different) ),

    maplist(all_distinct, Blocks),

    fd_dom(Cell_r1c1, Dom),
    writeln(domain_r1c1_before_labeling(Dom)),

    maplist(label, Grid),
    writeln(after_labeling(Grid)).

:- test, halt.
:- writeln(failed_overall), halt.
