typedef struct Outer {
  struct Middle {
    struct Inner {
      int value;
    } inner;
  } middle;
} OuterType;
