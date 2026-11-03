#define D typedef int U;
#define R8(x) x x x x x x x x
#define R9(x) x x x x x x x x x
#define R10(x) x x x x x x x x x x
#define R90(x) R9(R10(x))
#define R100(x) R10(R10(x))
#define R900(x) R9(R100(x))
#define R1000(x) R10(R100(x))
int main() {
  R1000(D) R900(D) R90(D) R8(D)
  return 0;
}
