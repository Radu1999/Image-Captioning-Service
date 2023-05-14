from lavis.models import load_model_and_preprocess
import pickle
import torch
import redis


def get_model_from_redis(redis_conn):

    part1 = redis_conn.get('caption_model_p1')
    if part1 is None:
        return None
    part2 = redis_conn.get('caption_model_p1')
    if part2 is None:
        return None

    return part1 + part2


class ModelLoader:
    def __init__(self):
        # Set the device to use
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        redis_conn = redis.Redis(host='redis', port=6379, socket_timeout=60)

        try:
            redis_conn.ping()
            conn_succ = True
        except redis.exceptions.ConnectionError:
            conn_succ = False

        # Check if the model is in Redis
        self.model = None
        self.vis_processors = None
        if conn_succ:
            self.model = get_model_from_redis(redis_conn)
            self.vis_processors = redis_conn.get('vis_processors')

        # if not in redis, load it and store it to redis
        if self.model is None or self.vis_processors is None:
            self.model, self.vis_processors, _ = load_model_and_preprocess(name="blip_caption",
                                                                           model_type="base_coco", is_eval=True,
                                                                                device=self.device)
            if conn_succ:
                self.store_model_redis(redis_conn)
                redis_conn.set('vis_processors', pickle.dumps(self.vis_processors))
        else:
            print('from redis')
            self.model = pickle.loads(self.model)
            self.vis_processors = pickle.loads(self.vis_processors)

    def get_model(self):
        return self.model

    def get_vis_processors(self):
        return self.vis_processors

    def predict(self, image):
        # Forward pass through the model
        with torch.no_grad():
            image = self.vis_processors["eval"](image).unsqueeze(0).to(self.device)
            # generate caption
            answer = self.model.generate({"image": image})
        return answer

    def store_model_redis(self, redis_conn):
        pickle_model = pickle.dumps(self.model)

        half_length = len(pickle_model) // 2
        part1 = pickle_model[:half_length]
        part2 = pickle_model[half_length:]

        redis_conn.set('caption_model_p1', part1)
        redis_conn.set('caption_model_p2', part2)

