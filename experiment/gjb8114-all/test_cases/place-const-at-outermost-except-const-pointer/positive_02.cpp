// 测试：常数指针声明是 const 紧邻指针的唯一合法写法
int a = 42;

int main() {
    int *const p = &a;
    *p = 7;
    return *p;
}
