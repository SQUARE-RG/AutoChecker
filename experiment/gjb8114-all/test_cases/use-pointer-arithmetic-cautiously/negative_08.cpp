struct Item { int value; };

int main() {
    Item items[2] = {{1}, {2}};
    Item *p = items;
    int v = (p + 1)->value;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-3-3]
    return v;
}
