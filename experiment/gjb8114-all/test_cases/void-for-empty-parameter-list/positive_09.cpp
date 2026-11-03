struct Widget {
    int id;
    int getId(void);
};

int Widget::getId(void) {
    return id;
}

int main(void) {
    Widget w{7};
    return w.getId();
}
