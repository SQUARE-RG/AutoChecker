struct A {
  struct B {
    struct C {
      int x = [] {
        struct D {}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-5]
        return 0;
      }();
    };
  };
};

int main() {
  A::B::C c;
  (void)c;
  return 0;
}
