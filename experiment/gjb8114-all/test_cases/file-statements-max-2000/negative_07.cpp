#define G goto end;
#define R10(x) x x x x x x x x x x
#define R100(x) R10(R10(x))
#define R1000(x) R10(R100(x))
void f() {
  R1000(G) R1000(G) G // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-2-1]
end: ;
}
int main() {
  return 0;
}
