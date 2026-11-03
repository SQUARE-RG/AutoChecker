class Widget {
public:
    Widget() { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-4]
        width = 1;
        height = 2;
    }
private:
    int width;
    int height;
    int depth;
};

int main() {
    Widget w;
    (void)w;
    return 0;
}
