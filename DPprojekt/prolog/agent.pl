% ============================================================================
% POJEDNOSTAVLJENI PROLOG AI AGENT za Into The Breach
% ============================================================================

% Glavni predikat - nalazi najbolju akciju
best_action(GameState, Action) :-
    GameState = game_state(Player, Enemies, Terrain, _ActionsLeft, GridSize),
    
    % Generiraj sve moguće akcije
    findall(
        scored_action(Priority, Type, Details),
        possible_action(Player, Enemies, Terrain, GridSize, Type, Priority, Details),
        Actions
    ),
    
    % Sortiraj po prioritetu (viši je bolji)
    sort(1, @>=, Actions, SortedActions),
    
    % Uzmi najbolju akciju
    (SortedActions = [scored_action(_, BestType, BestDetails) | _] ->
        format_action(BestType, BestDetails, Action)
    ;
        Action = no_action
    ).

% ============================================================================
% GENERIRANJE MOGUĆIH AKCIJA - POJEDNOSTAVLJENO
% ============================================================================

% Range attack - NAJVIŠI prioritet
possible_action(Player, Enemies, Terrain, _GridSize, range_attack, Priority, Details) :-
    Player = player(PX, PY, _PHP),
    member(Enemy, Enemies),
    Enemy = enemy(_Type, EX, EY, EHP),
    EHP > 0,
    
    % Check range (distance 1-2, grid distance)
    grid_distance(PX, PY, EX, EY, Distance),
    Distance >= 1,
    Distance =< 2,
    
    % Check line of sight
    has_line_of_sight(PX, PY, EX, EY, Terrain),
    
    % Viši prioritet za bliže neprijatelje
    Priority is 90 - Distance * 5 - EHP * 3,
    
    Details = attack(EX, EY, 1).

% Melee attack - VISOK prioritet kada je enemy adjacent
possible_action(Player, Enemies, _Terrain, _GridSize, melee_attack, Priority, Details) :-
    Player = player(PX, PY, _PHP),
    member(Enemy, Enemies),
    Enemy = enemy(_Type, EX, EY, EHP),
    EHP > 0,
    
    % Enemy must be adjacent (grid distance 1 - uključuje dijagonale)
    grid_distance(PX, PY, EX, EY, 1),
    
    % VISOK prioritet - melee radi više damage (2 vs 1)
    Priority is 95 - EHP * 3,
    
    Details = attack(EX, EY, 2).

% Movement - uvijek idi prema najbližem neprijatelju
possible_action(Player, Enemies, Terrain, GridSize, move, Priority, Details) :-
    Player = player(PX, PY, _PHP),
    
    % Generate possible positions (8-directional)
    member((DX, DY), [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]),
    NewX is PX + DX,
    NewY is PY + DY,
    
    % Check validity
    in_bounds(NewX, NewY, GridSize),
    get_terrain_at(Terrain, NewX, NewY, TerrainType),
    TerrainType = 0,  % Grass
    \+ position_occupied(NewX, NewY, Enemies),
    
    % Prioritet - što bliže neprijatelju, to bolje
    calculate_move_priority(Enemies, NewX, NewY, Priority),
    
    Details = move_to(NewX, NewY).

% ============================================================================
% HELPER PREDIKATI
% ============================================================================

% Grid distance (Chebyshev distance)
grid_distance(X1, Y1, X2, Y2, Distance) :-
    DX is abs(X1 - X2),
    DY is abs(Y1 - Y2),
    Distance is max(DX, DY).

% Check bounds
in_bounds(X, Y, GridSize) :-
    X >= 0, X < GridSize,
    Y >= 0, Y < GridSize.

% Get terrain type at position
get_terrain_at(Terrain, X, Y, Type) :-
    nth0(Y, Terrain, Row),
    nth0(X, Row, Type).

% Check line of sight - samo planine blokiraju
has_line_of_sight(X1, Y1, X2, Y2, Terrain) :-
    % Jednostavna Bresenham-like provjera
    DX is abs(X2 - X1),
    DY is abs(Y2 - Y1),
    SX is sign(X2 - X1),
    SY is sign(Y2 - Y1),
    check_line(X1, Y1, X2, Y2, DX, DY, SX, SY, DX - DY, Terrain).

check_line(X, Y, X, Y, _DX, _DY, _SX, _SY, _Err, _Terrain) :- !.
check_line(X1, Y1, X2, Y2, DX, DY, SX, SY, Err, Terrain) :-
    % Skip start and end positions
    (\+ (X1 = X2, Y1 = Y2) ->
        (get_terrain_at(Terrain, X1, Y1, Type),
         Type \= 1)  % Not mountain
    ; true),
    
    % Calculate next position
    E2 is 2 * Err,
    (E2 > -DY ->
        NewErr1 is Err - DY,
        NewX is X1 + SX
    ;
        NewErr1 = Err,
        NewX = X1
    ),
    (E2 < DX ->
        NewErr is NewErr1 + DX,
        NewY is Y1 + SY
    ;
        NewErr = NewErr1,
        NewY = Y1
    ),
    
    check_line(NewX, NewY, X2, Y2, DX, DY, SX, SY, NewErr, Terrain).

% Check if position is occupied by enemy
position_occupied(X, Y, Enemies) :-
    member(enemy(_Type, X, Y, HP), Enemies),
    HP > 0.

% Calculate movement priority - jednostavno, što bliže neprijatelju to bolje
calculate_move_priority(Enemies, NewX, NewY, Priority) :-
    % Nađi najbližeg neprijatelja
    findall(
        Dist,
        (
            member(enemy(_Type, EX, EY, EHP), Enemies),
            EHP > 0,
            grid_distance(NewX, NewY, EX, EY, Dist)
        ),
        Distances
    ),
    
    (Distances \= [] ->
        min_list(Distances, MinDist),
        % Što bliže, to viši prioritet (ali manji od attack-a)
        Priority is 50 - MinDist * 5
    ;
        Priority = 30
    ).

% Sign function
sign(X, 1) :- X > 0, !.
sign(X, -1) :- X < 0, !.
sign(0, 0).

% ============================================================================
% FORMATIRANJE AKCIJE ZA PYTHON
% ============================================================================

format_action(move, move_to(X, Y), move(X, Y)).
format_action(melee_attack, attack(X, Y, Dmg), melee_attack(X, Y, Dmg)).
format_action(range_attack, attack(X, Y, Dmg), range_attack(X, Y, Dmg)).
