namespace {
struct Widget {
    friend int widget_area(Widget) { return 42; }
};
}

int main() {
    Widget w;
    return widget_area(w);
}
