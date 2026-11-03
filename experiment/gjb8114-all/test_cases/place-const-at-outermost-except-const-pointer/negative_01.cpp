// 测试：指针声明中 const 未置于类型说明最外层
int a = 42;

int main() {
    int const *p = &a; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-2]
    return *p;
}
