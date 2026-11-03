struct A {
  struct B {
    int x = [] {
      struct C {};
      return 0;
    }();
  };
};

int main() {
  A::B b;
  return b.x;
}
