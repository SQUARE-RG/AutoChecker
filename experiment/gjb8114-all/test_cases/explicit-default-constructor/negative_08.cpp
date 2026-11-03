int main() {
    class Local { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-2]
    public:
        void set(int v) { value = v; }
        int get() const { return value; }
    private:
        int value;
    };

    Local obj;
    obj.set(4);
    return obj.get();
}
