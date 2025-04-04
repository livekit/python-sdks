import React, { useEffect, useState } from 'react';
import {
  LiveKitRoom,
  TrackToggle,
  BarVisualizer,
  useVoiceAssistant,
  RoomAudioRenderer,
  useConnectionState,
  DisconnectButton,
} from '@livekit/components-react';
import { Track } from 'livekit-client';
import '@livekit/components-styles';
import './App.css';


export async function fetchJoinInfo(): Promise<{ url: string; token: string }> {
  const invoke = (window as any).google?.colab?.kernel?.invokeFunction;
  if (invoke) {
    const res = await invoke("create_join_token", []);
    return res.data["application/json"];
  } else if ((window as any).jupyterFetchJoinToken) {
    return await (window as any).jupyterFetchJoinToken();
  } else if (import.meta.env.MODE === "development") {
    // use env variables
    const url = import.meta.env.VITE_LIVEKIT_URL;
    const token = import.meta.env.VITE_LIVEKIT_TOKEN;
    return { url: url, token: token };
  } else {
    throw new Error("No Colab or Jupyter kernel function available");
  }
}


function CloseIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M3.33398 3.33334L12.6673 12.6667M12.6673 3.33334L3.33398 12.6667"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="square"
      />
    </svg>
  );
}

const ConnectedContent: React.FC<{ onDisconnect: () => void }> = ({ onDisconnect }) => {
  const connectionState = useConnectionState();
  const { state: agentState, audioTrack: agentTrack } = useVoiceAssistant();

  console.log(agentState);



  return (
    <div className="content">
      <RoomAudioRenderer />
      <header className="header">
        <div className="header-left">
          <h2>livekit-rtc</h2>
          <span className={`connection-state ${['connecting', 'disconnected'].includes(connectionState) ? 'state-inactive' : ''}`}>
            {connectionState}
          </span>
        </div>
        <div className="header-controls">
          <DisconnectButton onClick={onDisconnect}><CloseIcon />Disconnect</DisconnectButton>
        </div>
      </header>
      <div className="controls">
        <div className="controls-row">
          <TrackToggle
            source={Track.Source.Microphone}
            initialState={false}
          >
            Toggle Microphone
          </TrackToggle>

          <div className="visualizer mic-visualizer" style={{ height: '40px' }}>
            {/* <BarVisualizer
              barCount={15}
              trackRef={localTrackRef}
              options={{ minHeight: 40, maxHeight: 40 }}
            /> */}
          </div>
        </div>

        <div className="visualizer agent-visualizer" style={{ height: '40px', width: '100%' }}>
          <BarVisualizer
            state={agentState}
            barCount={8}
            trackRef={agentTrack}
            options={{ minHeight: 60, maxHeight: 60 }}
          />
        </div>
      </div>
    </div>
  );
};

const App = () => {
  const [joinInfo, setJoinInfo] = useState<{ url: string; token: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(true);

  useEffect(() => {
    fetchJoinInfo()
      .then((info) => setJoinInfo(info))
      .catch((err) => setError(err.message));
  }, []);

  if (error) return <div>Error: {error}</div>;

  if (!joinInfo) return <div>Loading...</div>;

  if (!isConnected) {
    return (
      <div className="content">
        <header className="header">
          <div className="header-left">
            <h2>livekit-rtc</h2>
            <span className="state-inactive">disconnected</span>
          </div>
          <div className="header-controls">
            <span className="state-inactive">Re-run the cell to connect</span>
          </div>
        </header>
      </div>
    );
  }

  return (
    <LiveKitRoom
      serverUrl={joinInfo.url}
      token={joinInfo.token}
      onError={(err) => setError(err.message)}
    >
      <ConnectedContent onDisconnect={() => setIsConnected(false)} />
    </LiveKitRoom>
  );
};
export default App;