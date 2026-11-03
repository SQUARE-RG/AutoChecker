// 测试：非指针变量声明中 const 未置于类型说明最外层

int main() {
    int const b = 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-2]
    return b;
}
