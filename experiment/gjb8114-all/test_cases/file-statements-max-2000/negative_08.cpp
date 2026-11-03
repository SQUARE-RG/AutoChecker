#define D typedef int U;
#define R10(x) x x x x x x x x x x
#define R100(x) R10(R10(x))
#define R1000(x) R10(R100(x))
int main() {
  R1000(D) R1000(D) D // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-2-1]
  return 0;
}
