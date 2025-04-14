import tensorflow as tf

# Load with compatibility mode
model = tf.keras.models.load_model('models/model2.h5', compile=False)

# Save it again in a compatible format
model.save('models/converted_model.h5')
