// negative_01.cpp
// 场景：用 goto 向前跳转跳过一段赋值逻辑。
int main() {
    int value = 0;
    goto cleanup; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-5-1]
    value = 42;
cleanup:
    return value;
}
