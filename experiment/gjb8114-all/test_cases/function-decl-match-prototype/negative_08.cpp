auto add(int lhs) -> int; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-14]

auto add(int rhs) -> int
{
    return rhs + 1;
}
