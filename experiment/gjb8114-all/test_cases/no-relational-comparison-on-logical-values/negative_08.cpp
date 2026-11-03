constexpr bool high = true;
constexpr bool low = false;

static_assert(high > low); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-1]

int main() {
    return 0;
}
