import React, { useEffect, useState } from 'react';
import {
  LiveKitRoom,
  BarVisualizer,
  useVoiceAssistant,
  RoomAudioRenderer,
  useConnectionState,
  DisconnectButton,
  useStartAudio,
  VoiceAssistantControlBar,
} from '@livekit/components-react';
import '@livekit/components-styles';
import './App.css';
import type { SVGProps } from 'react';
import { ConnectionState } from 'livekit-client';


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


const LeaveIcon = (props: SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={16} height={16} fill="none" {...props}>
    <path
      fill="currentColor"
      fillRule="evenodd"
      d="M2 2.75A2.75 2.75 0 0 1 4.75 0h6.5A2.75 2.75 0 0 1 14 2.75v10.5A2.75 2.75 0 0 1 11.25 16h-6.5A2.75 2.75 0 0 1 2 13.25v-.5a.75.75 0 0 1 1.5 0v.5c0 .69.56 1.25 1.25 1.25h6.5c.69 0 1.25-.56 1.25-1.25V2.75c0-.69-.56-1.25-1.25-1.25h-6.5c-.69 0-1.25.56-1.25 1.25v.5a.75.75 0 0 1-1.5 0v-.5Z"
      clipRule="evenodd"
    />
    <path
      fill="currentColor"
      fillRule="evenodd"
      d="M8.78 7.47a.75.75 0 0 1 0 1.06l-2.25 2.25a.75.75 0 1 1-1.06-1.06l.97-.97H1.75a.75.75 0 0 1 0-1.5h4.69l-.97-.97a.75.75 0 0 1 1.06-1.06l2.25 2.25Z"
      clipRule="evenodd"
    />
  </svg>
);

const ConnectedContent: React.FC<{ onDisconnect: () => void }> = ({ onDisconnect }) => {
  const connectionState = useConnectionState();
  const { state: agentState, audioTrack: agentTrack } = useVoiceAssistant();
  const { canPlayAudio } = useStartAudio({ props: {} }); // why do I need props..?

  return (
    <div className="content">
      <header className="header">
        <div className="header-left">
          <h2>livekit-rtc</h2>
          <span className={`connection-state ${['connecting', 'disconnected'].includes(connectionState) ? 'state-inactive' : ''}`}>
            {connectionState}
          </span>
        </div>
        <div className="header-controls">
          <DisconnectButton onClick={onDisconnect}><LeaveIcon />Disconnect</DisconnectButton>
        </div>
      </header>
      <div className="controls">
        <VoiceAssistantControlBar controls={{ microphone: true, leave: false }} />

        {canPlayAudio && connectionState == ConnectionState.Connected && <div className="agent-visualizer">
          <BarVisualizer
            state={agentState}
            barCount={15}
            trackRef={agentTrack}
            options={{ minHeight: 30, maxHeight: 30 }}
          />
        </div>}
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
      <RoomAudioRenderer />
    </LiveKitRoom>
  );
};
export default App;