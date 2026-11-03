struct Widget {
    int id;
    int getId(void);
};

int Widget::getId() { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-23]
    return id;
}

int main(void) {
    Widget w{7};
    return w.getId();
}
