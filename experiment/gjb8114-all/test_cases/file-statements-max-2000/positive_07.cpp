#define G goto end;
#define R5(x) x x x x x
#define R9(x) x x x x x x x x x
#define R10(x) x x x x x x x x x x
#define R90(x) R9(R10(x))
#define R100(x) R10(R10(x))
#define R900(x) R9(R100(x))
#define R1000(x) R10(R100(x))
void f() {
  R1000(G) R900(G) R90(G) R5(G)
end: ;
}
int main() {
  return 0;
}
