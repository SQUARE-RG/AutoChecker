namespace {
struct Widget {
    friend int widget_area(Widget) { return 42; } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-3]
};
}

int main() {
    Widget w;
    (void)w;
    return 0;
}
