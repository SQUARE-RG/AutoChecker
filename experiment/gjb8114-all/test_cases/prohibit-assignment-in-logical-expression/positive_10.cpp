int main() {
    int i = 0;
    int n = 5;
    bool flag = false;
    while (i < n || flag) {
        flag = (i == 2);
        ++i;
    }
    return 0;
}
