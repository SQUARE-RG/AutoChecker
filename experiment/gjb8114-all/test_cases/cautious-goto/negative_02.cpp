// negative_02.cpp
// 场景：通过向后 goto 回到标签形成重试逻辑。
int main() {
    int attempts = 0;
retry:
    if (attempts < 3) {
        ++attempts;
        goto retry; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-5-1]
    }
    return attempts;
}
