# PAL 0.1 syntax specification

## Grammar

```
document := pal@pack[head|center]
head := atom > atom > ... > atom
atom := identifier
```

Example:

```
pal@palindrome-jiugong-v0.1[A>B>C>D|e]
```

## Storage rule

Only the independent inward path is stored:

```
[A,B,C,D,e]
```

The logical expanded sequence is generated lazily:

```
A,B,C,D,e,D,C,B,A
```

## Address rule

A stored head position directly determines the complementary end position:

```
i -> L-1-i
```

without scanning the generated tail.

## Compute rule

The storage representation is projected into a 3x3 center-symmetric carrier:

```
A B C
D e D
C B A
```

This prototype only defines the mapping contract. The emergence operator remains an experimental layer and must preserve closure before committing back to storage.
