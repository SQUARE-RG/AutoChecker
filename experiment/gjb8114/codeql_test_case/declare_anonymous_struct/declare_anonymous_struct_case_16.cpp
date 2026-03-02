#include <stdio.h>

struct Variant {
    int type;
    union {
        struct IntData {
            int value;
        } int_data;
        struct FloatData {
            float value;
        } float_data;
    } data;  // 符合：联合体中的命名结构体
};

int main(void) {
    struct Variant v;
    v.data.int_data.value = 42;
    return 0;
}