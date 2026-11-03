typedef struct Outer {
  struct Middle {
    struct Inner {
      struct Deep { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-5]
        int value;
      } deep;
    } inner;
  } middle;
} OuterType;
